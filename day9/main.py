from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from murf import Murf
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import time
import assemblyai as aai
import os
import uuid
import tempfile
import requests
import json
from typing import Dict, Any, Optional
from fastapi import Body
import httpx
import google.generativeai as genai


load_dotenv()

app = FastAPI(title="Echo Bot v2 with Murf TTS and Gemini LLM")

# Mount static files (HTML, JS, etc.)
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Get from environment variables
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize AssemblyAI
aai.settings.api_key = ASSEMBLYAI_API_KEY

# Initialize Murf SDK
client = Murf(api_key=MURF_API_KEY) if MURF_API_KEY else None

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
else:
    gemini_model = None

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic model for request body
class TextRequest(BaseModel):
    text: str

# NEW: Pydantic model for LLM query request
class LLMQueryRequest(BaseModel):
    text: str

# NEW: LLM Query endpoint using Gemini API

@app.post("/llm/query")
async def llm_query(
    audio_file: UploadFile = File(None),
    text: Optional[str] = Form(None),
    voiceId: Optional[str] = Form(default="en-US-natalie")
):
    """
    Enhanced LLM Query endpoint that:
    1. Accepts either audio file OR text input
    2. If audio: transcribes → sends to Gemini → generates TTS response
    3. If text: sends to Gemini → generates TTS response
    4. Handles Murf's 3000 character limit
    """
    try:
        if not gemini_model:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        input_text = ""
        
        # Step 1: Get input text (from audio or direct text)
        if audio_file:
            print(f"Processing audio input: {audio_file.filename}")
            
            # Transcribe audio using AssemblyAI
            audio_bytes = await audio_file.read()
            print(f"Audio file size: {len(audio_bytes)} bytes")
            
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_bytes)
            
            if transcript.status == aai.TranscriptStatus.error:
                raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
            
            input_text = transcript.text
            print(f"Transcribed text: {input_text}")
            
        elif text:
            input_text = text.strip()
            print(f"Direct text input: {input_text}")
        else:
            raise HTTPException(status_code=400, detail="Either audio file or text input is required")
        
        if not input_text:
            raise HTTPException(status_code=400, detail="No valid input detected")
        
        # Step 2: Generate LLM response with Gemini
        print(f"Querying Gemini with: {input_text}")
        
        # Add instruction to keep responses concise for TTS
        prompt = f"Please provide a conversational response (maximum 2500 characters) to: {input_text}"
        
        response = gemini_model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="No response generated from Gemini")
        
        llm_response = response.text.strip()
        print(f"Gemini response length: {len(llm_response)} chars")
        
        # Step 3: Handle Murf's 3000 character limit
        audio_urls = []
        
        if len(llm_response) <= 3000:
            # Single request
            audio_url = await generate_murf_audio(llm_response, voiceId)
            audio_urls.append(audio_url)
        else:
            # Split into chunks
            chunks = split_text_for_murf(llm_response, 2800)  # Leave buffer
            print(f"Split response into {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
                audio_url = await generate_murf_audio(chunk, voiceId)
                audio_urls.append(audio_url)
        
        return {
            "input": input_text,
            "response": llm_response,
            "model": "gemini-1.5-flash",
            "voice_id": voiceId,
            "audio_urls": audio_urls,  # List of audio URLs
            "audio_url": audio_urls[0] if audio_urls else None,  # Primary audio for compatibility
            "chunks_count": len(audio_urls),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error in llm_query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM query failed: {str(e)}")

# Legacy endpoint for direct text-to-speech
@app.post("/generate-audio/")
async def generate_audio(request: TextRequest):
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Murf API key not configured")
            
        audio_res = client.text_to_speech.generate(
            text=request.text,
            voice_id="en-US-terrell"
        )
        return {"audio_url": audio_res.audio_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Upload audio endpoint
@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    extension = file.filename.split(".")[-1] if "." in file.filename else "webm"
    new_filename = f"audio_{timestamp}_{unique_id}.{extension}"

    file_path = UPLOAD_DIR / new_filename
    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "filename": new_filename,
        "content_type": file.content_type,
        "size": len(contents),
        "file_path": str(file_path)
    }

# Transcribe file endpoint using AssemblyAI SDK
@app.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...)):
    try:
        # Read contents of the uploaded file
        audio_bytes = await file.read()

        # Use AssemblyAI SDK to transcribe directly from bytes
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_bytes)

        if transcript.status == aai.TranscriptStatus.error:
            raise RuntimeError(f"Transcription failed: {transcript.error}")

        return {"transcript": transcript.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Main echo endpoint - FIXED VERSION
@app.post("/tts/echo")
async def tts_echo(
    audio_file: UploadFile = File(...), 
    voiceId: Optional[str] = Form(default="en-US-natalie")
):
    """
    Echo endpoint that:
    1. Accepts audio file and optional voice ID
    2. Transcribes using AssemblyAI SDK
    3. Generates TTS using Murf SDK with selected voice
    4. Returns audio URL
    """
    try:
        print(f"Processing audio file: {audio_file.filename}")
        print(f"Selected voice: {voiceId}")
        
        # Step 1: Read audio file
        audio_bytes = await audio_file.read()
        print(f"Audio file size: {len(audio_bytes)} bytes")
        
        # Step 2: Transcribe audio using AssemblyAI SDK
        print("Starting transcription with AssemblyAI...")
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_bytes)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
        
        transcribed_text = transcript.text
        print(f"Transcription completed: {transcribed_text}")
        
        if not transcribed_text or transcribed_text.strip() == "":
            return JSONResponse(
                status_code=400, 
                content={"error": "No speech detected in audio"}
            )
        
        # Step 3: Generate TTS using Murf SDK with selected voice
        print(f"Generating TTS with Murf using voice: {voiceId}")
        if not client:
            raise HTTPException(status_code=500, detail="Murf API key not configured")
        
        try:
            # Use Murf SDK for TTS generation with selected voice
            audio_res = client.text_to_speech.generate(
                text=transcribed_text,
                voice_id=voiceId  # Use the selected voice
            )
            
            audio_url = audio_res.audio_file
            print(f"TTS generation completed: {audio_url}")
            
            return {
                "text": transcribed_text,
                "audio_url": audio_url,
                "voice_id": voiceId,
                "status": "success"
            }
            
        except Exception as murf_error:
            print(f"Murf SDK error: {str(murf_error)}")
            # Fallback to direct API call if SDK fails
            return await generate_murf_tts_fallback(transcribed_text, voiceId)
        
    except Exception as e:
        print(f"Error in tts_echo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

async def generate_murf_tts_fallback(text: str, voice_id: str = "en-US-natalie") -> Dict[str, Any]:
    """
    Fallback method using direct Murf API calls with voice selection
    """
    try:
        print(f"Using Murf API fallback method with voice: {voice_id}")
        
        # Murf API direct call
        headers = {
            "Authorization": f"Bearer {MURF_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "voiceId": voice_id,  # Use the selected voice
            "style": "Conversational",
            "text": text,
            "rate": 0,
            "pitch": 0,
            "sampleRate": 22050,
            "format": "MP3",
            "channelType": "MONO",
            "pronunciationDictionary": {},
            "encodeAsBase64": False
        }
        
        response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Murf API error: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Murf API error: {response.text}"
            )
        
        result = response.json()
        
        if "audioFile" not in result:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from Murf API - no audio file"
            )
        
        return {
            "text": text,
            "audio_url": result["audioFile"],
            "voice_id": voice_id,
            "status": "success"
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Request to Murf API failed: {str(e)}")
    except Exception as e:
        print(f"Fallback TTS generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

# Get available voices from Murf
@app.get("/voices")
async def get_available_voices():
    """
    Get available voices from Murf API
    """
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Murf API key not configured")
            
        # Try to use SDK method first
        try:
            voices = client.voices.list()
            return {"voices": voices}
        except:
            # Fallback to direct API call
            headers = {"Authorization": f"Bearer {MURF_API_KEY}"}
            response = requests.get(
                "https://api.murf.ai/v1/speech/voices",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch voices: {response.text}"
                )
            
            return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")

# Health check endpoint - UPDATED to include Gemini status
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "assemblyai_configured": bool(ASSEMBLYAI_API_KEY),
        "murf_configured": bool(MURF_API_KEY and client),
        "murf_sdk_available": client is not None,
        "gemini_configured": bool(GEMINI_API_KEY and gemini_model),
        "gemini_model": "gemini-1.5-flash" if gemini_model else None
    }

async def generate_murf_audio(text: str, voice_id: str = "en-US-natalie") -> str:
    """
    Generate audio using Murf API for given text
    Returns the audio URL
    """
    try:
        if not client:
            # Fallback to direct API call
            headers = {
                "Authorization": f"Bearer {MURF_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "voiceId": voice_id,
                "style": "Conversational",
                "text": text,
                "rate": 0,
                "pitch": 0,
                "sampleRate": 22050,
                "format": "MP3",
                "channelType": "MONO",
                "pronunciationDictionary": {},
                "encodeAsBase64": False
            }
            
            response = requests.post(
                "https://api.murf.ai/v1/speech/generate",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Murf API error: {response.text}"
                )
            
            result = response.json()
            return result["audioFile"]
        
        else:
            # Use Murf SDK
            audio_res = client.text_to_speech.generate(
                text=text,
                voice_id=voice_id
            )
            return audio_res.audio_file
            
    except Exception as e:
        print(f"Murf audio generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

# Helper function to split text for Murf's character limit
def split_text_for_murf(text: str, max_chars: int = 2800) -> list:
    """
    Split text into chunks that fit within Murf's character limit
    Tries to split at sentence boundaries when possible
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentences first
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence += "."  # Add period back
        
        # If adding this sentence exceeds limit, save current chunk and start new one
        if len(current_chunk + sentence) > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # Single sentence is too long, force split by words
                words = sentence.split()
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk + " " + word) > max_chars:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                            temp_chunk = word
                        else:
                            # Single word too long, force character split
                            chunks.append(word[:max_chars])
                            temp_chunk = word[max_chars:]
                    else:
                        temp_chunk += " " + word if temp_chunk else word
                
                if temp_chunk:
                    current_chunk = temp_chunk
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)