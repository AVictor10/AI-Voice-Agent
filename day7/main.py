# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from murf import Murf
# from dotenv import load_dotenv
# from fastapi import UploadFile, File
# from pathlib import Path
# from datetime import datetime
# import assemblyai as aai
# import os
# import uuid
# import tempfile
# import requests

# load_dotenv()

# app = FastAPI()

# # Mount static files (HTML, JS, etc.)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/")
# async def root():
#     return FileResponse("static/index.html")

# # CORS (optional)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Pydantic model for request body
# class TextRequest(BaseModel):
#     text: str

# # Initialize Murf SDK
# MURF_API_KEY = os.getenv("MURF_API_KEY")
# client = Murf(api_key=MURF_API_KEY)

# @app.post("/generate-audio/")
# async def generate_audio(request: TextRequest):
#     try:
#         audio_res = client.text_to_speech.generate(
#             text=request.text,
#             voice_id="en-US-terrell"
#         )
#         return {"audio_url": audio_res.audio_file}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)

# @app.post("/upload-audio/")
# async def upload_audio(file: UploadFile = File(...)):
    
#     timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#     unique_id = uuid.uuid4().hex[:6]
#     extension = file.filename.split(".")[-1]
#     new_filename = f"audio_{timestamp}_{unique_id}.{extension}"

#     file_path = UPLOAD_DIR / new_filename
#     contents = await file.read()

#     with open(file_path, "wb") as f:
#         f.write(contents)

#     return {
#         "filename": new_filename,
#         "content_type": file.content_type,
#         "size": len(contents)
#     }

# #Transcribe File Logic

# aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# @app.post("/transcribe/file")
# async def transcribe_file(file: UploadFile = File(...)):
#     try:
#         # Read contents of the uploaded file
#         audio_bytes = await file.read()

#         # Use AssemblyAI SDK to transcribe directly from bytes
#         transcriber = aai.Transcriber()
#         transcript = transcriber.transcribe(audio_bytes)

#         if transcript.status == "error":
#             raise RuntimeError(f"Transcription failed: {transcript.error}")

#         return {"transcript": transcript.text}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# # Day 7 changes

# # import tempfile


# @app.post("/tts/echo")
# async def tts_echo(audio_file: UploadFile = File(...)):
#     try:
#         # Step 1: Send audio to AssemblyAI for transcription
#         headers = {"authorization": ASSEMBLY_API_KEY}
#         transcript_res = requests.post(
#             "https://api.assemblyai.com/v2/transcript",
#             json={"audio_url": await upload_to_temp_host(audio_file)},
#             headers=headers
#         ).json()
#         transcript_id = transcript_res["id"]

#         # Poll until transcription completes
#         while True:
#             poll_res = requests.get(
#                 f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
#                 headers=headers
#             ).json()
#             if poll_res["status"] == "completed":
#                 text = poll_res["text"]
#                 break
#             elif poll_res["status"] == "error":
#                 return JSONResponse({"error": poll_res["error"]}, status_code=500)

#         # Step 2: Send text to Murf TTS (fixed voice)
#         murf_headers = {
#             "Authorization": f"Bearer {MURF_API_KEY}",
#             "Content-Type": "application/json"
#         }
#         murf_payload = {
#             "voiceId": "en-US-natalie",  # fixed voice
#             "text": text
#         }
#         murf_res = requests.post(
#             "https://api.murf.ai/v1/speech",
#             headers=murf_headers,
#             json=murf_payload
#         ).json()

#         audio_url = murf_res.get("audioFile")

#         return {"text": text, "audio_url": audio_url}

#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)


# # --- Helper: Upload to temp host (AssemblyAI needs a public URL) ---
# async def upload_to_temp_host(file: UploadFile) -> str:
#     upload_url = "https://api.assemblyai.com/v2/upload"
#     headers = {"authorization": ASSEMBLY_API_KEY}

#     data = await file.read()
#     res = requests.post(upload_url, headers=headers, data=data)
#     res.raise_for_status()
#     return res.json()["upload_url"]

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from murf import Murf
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import assemblyai as aai
import os
import uuid
import tempfile
import requests
import json
from typing import Dict, Any, Optional

load_dotenv()

app = FastAPI(title="Echo Bot v2 with Murf TTS")

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

# Initialize AssemblyAI
aai.settings.api_key = ASSEMBLYAI_API_KEY

# Initialize Murf SDK
client = Murf(api_key=MURF_API_KEY) if MURF_API_KEY else None

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic model for request body
class TextRequest(BaseModel):
    text: str

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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "assemblyai_configured": bool(ASSEMBLYAI_API_KEY),
        "murf_configured": bool(MURF_API_KEY and client),
        "murf_sdk_available": client is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)