# from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Path
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, FileResponse
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from murf import Murf
# from dotenv import load_dotenv
# from pathlib import Path as PathLib
# from datetime import datetime
# from typing import Dict, List
# import time
# import assemblyai as aai
# import os
# import uuid
# import tempfile
# import requests
# import json
# from typing import Dict, Any, Optional
# from fastapi import Body
# import httpx
# import google.generativeai as genai


# load_dotenv()

# app = FastAPI(title="Echo Bot v2 with Murf TTS and Gemini LLM - Chat History Enabled")

# # Mount static files (HTML, JS, etc.)
# static_dir = PathLib("static")
# static_dir.mkdir(exist_ok=True)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/")
# async def root():
#     return FileResponse("static/index.html")

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Configuration - Get from environment variables
# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# MURF_API_KEY = os.getenv("MURF_API_KEY")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # ENHANCED: In-memory chat history storage - simple dictionary
# CHAT_HISTORY: Dict[str, List[Dict]] = {}

# def get_chat_history(session_id: str) -> List[Dict]:
#     """Get chat history for a session"""
#     return CHAT_HISTORY.get(session_id, [])

# def add_to_chat_history(session_id: str, role: str, content: str):
#     """Add a message to chat history"""
#     if session_id not in CHAT_HISTORY:
#         CHAT_HISTORY[session_id] = []
    
#     CHAT_HISTORY[session_id].append({
#         "role": role,
#         "content": content,
#         "timestamp": time.time()
#     })

# def format_chat_for_gemini(session_id: str, new_user_message: str) -> str:
#     """Format chat history for Gemini API"""
#     history = get_chat_history(session_id)
    
#     # Build conversation context
#     conversation = []
#     for msg in history[-10:]:  # Keep last 10 messages for context
#         if msg["role"] == "user":
#             conversation.append(f"User: {msg['content']}")
#         else:
#             conversation.append(f"Assistant: {msg['content']}")
    
#     # Add new user message
#     conversation.append(f"User: {new_user_message}")
    
#     # Create prompt with context
#     if len(conversation) == 1:
#         # First message in conversation
#         prompt = f"You are a helpful AI assistant. Please respond conversationally (maximum 2500 characters) to: {new_user_message}"
#     else:
#         # Continuing conversation
#         context = "\n".join(conversation[:-1])
#         prompt = f"""You are a helpful AI assistant. Here's our conversation so far:

# {context}

# Now the user says: {new_user_message}

# Please respond naturally and conversationally (maximum 2500 characters):"""
    
#     return prompt


# # Initialize AssemblyAI
# aai.settings.api_key = ASSEMBLYAI_API_KEY

# # Initialize Murf SDK
# client = Murf(api_key=MURF_API_KEY) if MURF_API_KEY else None

# # Initialize Gemini
# if GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)
#     gemini_model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
# else:
#     gemini_model = None

# # Create upload directory
# UPLOAD_DIR = PathLib("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)

# # Pydantic model for request body
# class TextRequest(BaseModel):
#     text: str

# # NEW: Pydantic model for LLM query request
# class LLMQueryRequest(BaseModel):
#     text: str

# # NEW: Chat History endpoint - The main conversational endpoint
# @app.post("/agent/chat/{session_id}")
# async def agent_chat(
#     session_id: str = Path(..., description="Session ID for chat history"),
#     audio_file: UploadFile = File(None),
#     text: Optional[str] = Form(None),
#     voiceId: Optional[str] = Form(default="en-US-natalie")
# ):
#     """
#     Enhanced Chat endpoint with persistent session history:
#     1. Accepts either audio file OR text input
#     2. Retrieves conversation history for session_id
#     3. If audio: transcribes → appends to chat history → sends to Gemini → adds response to history → generates TTS
#     4. If text: appends to chat history → sends to Gemini → adds response to history → generates TTS
#     5. Returns both text response and audio URL(s)
#     """
#     try:
#         if not gemini_model:
#             raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
#         input_text = ""
        
#         # Step 1: Get input text (from audio or direct text)
#         if audio_file:
#             print(f"[Session {session_id}] Processing audio input: {audio_file.filename}")
            
#             # Transcribe audio using AssemblyAI
#             audio_bytes = await audio_file.read()
#             print(f"[Session {session_id}] Audio file size: {len(audio_bytes)} bytes")
            
#             transcriber = aai.Transcriber()
#             transcript = transcriber.transcribe(audio_bytes)
            
#             if transcript.status == aai.TranscriptStatus.error:
#                 raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
            
#             input_text = transcript.text
#             print(f"[Session {session_id}] Transcribed text: {input_text}")
            
#         elif text:
#             input_text = text.strip()
#             print(f"[Session {session_id}] Direct text input: {input_text}")
#         else:
#             raise HTTPException(status_code=400, detail="Either audio file or text input is required")
        
#         if not input_text:
#             raise HTTPException(status_code=400, detail="No valid input detected")
        
#         # Step 2: Add user message to chat history
#         add_to_chat_history(session_id, "user", input_text)
#         print(f"[Session {session_id}] Added user message to history. Total messages: {len(get_chat_history(session_id))}")
        
#         # Step 3: Format conversation history and generate LLM response
#         formatted_prompt = format_chat_for_gemini(session_id, input_text)
#         print(f"[Session {session_id}] Querying Gemini with conversation context...")
        
#         response = gemini_model.generate_content(formatted_prompt)
        
#         if not response.text:
#             raise HTTPException(status_code=500, detail="No response generated from Gemini")
        
#         llm_response = response.text.strip()
#         print(f"[Session {session_id}] Gemini response length: {len(llm_response)} chars")
        
#         # Step 4: Add assistant response to chat history
#         add_to_chat_history(session_id, "assistant", llm_response)
#         print(f"[Session {session_id}] Added assistant response to history. Total messages: {len(get_chat_history(session_id))}")
        
#         # Step 5: Generate TTS - Handle Murf's 3000 character limit
#         audio_urls = []
        
#         if len(llm_response) <= 3000:
#             # Single request
#             audio_url = await generate_murf_audio(llm_response, voiceId)
#             audio_urls.append(audio_url)
#         else:
#             # Split into chunks
#             chunks = split_text_for_murf(llm_response, 2800)  # Leave buffer
#             print(f"[Session {session_id}] Split response into {len(chunks)} chunks")
            
#             for i, chunk in enumerate(chunks):
#                 print(f"[Session {session_id}] Processing chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
#                 audio_url = await generate_murf_audio(chunk, voiceId)
#                 audio_urls.append(audio_url)
        
#         # Step 6: Get current conversation stats
#         history = get_chat_history(session_id)
#         conversation_length = len(history)
        
#         return {
#             "session_id": session_id,
#             "input": input_text,
#             "response": llm_response,
#             "model": "gemini-1.5-flash",
#             "voice_id": voiceId,
#             "audio_urls": audio_urls,  # List of audio URLs
#             "audio_url": audio_urls[0] if audio_urls else None,  # Primary audio for compatibility
#             "chunks_count": len(audio_urls),
#             "conversation_length": conversation_length,
#             "conversation_turns": conversation_length // 2,  # Pairs of user/assistant messages
#             "status": "success"
#         }
        
#     except Exception as e:
#         print(f"[Session {session_id}] Error in agent_chat: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Agent chat failed: {str(e)}")

# # NEW: Get conversation history for a session
# @app.get("/agent/history/{session_id}")
# async def get_conversation_history(session_id: str = Path(..., description="Session ID")):
#     """
#     Get conversation history for a specific session
#     """
#     try:
#         history = get_chat_history(session_id)
        
#         return {
#             "session_id": session_id,
#             "message_count": len(history),
#             "conversation_turns": len(history) // 2,
#             "history": history,
#             "status": "success"
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

# # NEW: Clear conversation history for a session
# @app.delete("/agent/history/{session_id}")
# async def clear_conversation_history(session_id: str = Path(..., description="Session ID")):
#     """
#     Clear conversation history for a specific session
#     """
#     try:
#         if session_id in CHAT_HISTORY:
#             del CHAT_HISTORY[session_id]
#             return {
#                 "session_id": session_id,
#                 "message": "Conversation history cleared",
#                 "status": "success"
#             }
#         else:
#             return {
#                 "session_id": session_id,
#                 "message": "No history found for this session",
#                 "status": "success"
#             }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")

# # NEW: List all active sessions
# @app.get("/agent/sessions")
# async def list_active_sessions():
#     """
#     List all active chat sessions
#     """
#     try:
#         sessions_info = []
#         for session_id, history in CHAT_HISTORY.items():
#             if history:  # Only include sessions with messages
#                 sessions_info.append({
#                     "session_id": session_id,
#                     "message_count": len(history),
#                     "conversation_turns": len(history) // 2,
#                     "last_message_time": history[-1]["timestamp"] if history else None,
#                     "created_time": history[0]["timestamp"] if history else None
#                 })
        
#         return {
#             "active_sessions": len(sessions_info),
#             "sessions": sessions_info,
#             "status": "success"
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


# # EXISTING: LLM Query endpoint (kept for backwards compatibility)
# @app.post("/llm/query")
# async def llm_query(
#     audio_file: UploadFile = File(None),
#     text: Optional[str] = Form(None),
#     voiceId: Optional[str] = Form(default="en-US-natalie")
# ):
#     """
#     Enhanced LLM Query endpoint that:
#     1. Accepts either audio file OR text input
#     2. If audio: transcribes → sends to Gemini → generates TTS response
#     3. If text: sends to Gemini → generates TTS response
#     4. Handles Murf's 3000 character limit
#     """
#     try:
#         if not gemini_model:
#             raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
#         input_text = ""
        
#         # Step 1: Get input text (from audio or direct text)
#         if audio_file:
#             print(f"Processing audio input: {audio_file.filename}")
            
#             # Transcribe audio using AssemblyAI
#             audio_bytes = await audio_file.read()
#             print(f"Audio file size: {len(audio_bytes)} bytes")
            
#             transcriber = aai.Transcriber()
#             transcript = transcriber.transcribe(audio_bytes)
            
#             if transcript.status == aai.TranscriptStatus.error:
#                 raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
            
#             input_text = transcript.text
#             print(f"Transcribed text: {input_text}")
            
#         elif text:
#             input_text = text.strip()
#             print(f"Direct text input: {input_text}")
#         else:
#             raise HTTPException(status_code=400, detail="Either audio file or text input is required")
        
#         if not input_text:
#             raise HTTPException(status_code=400, detail="No valid input detected")
        
#         # Step 2: Generate LLM response with Gemini
#         print(f"Querying Gemini with: {input_text}")
        
#         # Add instruction to keep responses concise for TTS
#         prompt = f"Please provide a conversational response (maximum 2500 characters) to: {input_text}"
        
#         response = gemini_model.generate_content(prompt)
        
#         if not response.text:
#             raise HTTPException(status_code=500, detail="No response generated from Gemini")
        
#         llm_response = response.text.strip()
#         print(f"Gemini response length: {len(llm_response)} chars")
        
#         # Step 3: Handle Murf's 3000 character limit
#         audio_urls = []
        
#         if len(llm_response) <= 3000:
#             # Single request
#             audio_url = await generate_murf_audio(llm_response, voiceId)
#             audio_urls.append(audio_url)
#         else:
#             # Split into chunks
#             chunks = split_text_for_murf(llm_response, 2800)  # Leave buffer
#             print(f"Split response into {len(chunks)} chunks")
            
#             for i, chunk in enumerate(chunks):
#                 print(f"Processing chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
#                 audio_url = await generate_murf_audio(chunk, voiceId)
#                 audio_urls.append(audio_url)
        
#         return {
#             "input": input_text,
#             "response": llm_response,
#             "model": "gemini-1.5-flash",
#             "voice_id": voiceId,
#             "audio_urls": audio_urls,  # List of audio URLs
#             "audio_url": audio_urls[0] if audio_urls else None,  # Primary audio for compatibility
#             "chunks_count": len(audio_urls),
#             "status": "success"
#         }
        
#     except Exception as e:
#         print(f"Error in llm_query: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"LLM query failed: {str(e)}")

        

# # Legacy endpoint for direct text-to-speech
# @app.post("/generate-audio/")
# async def generate_audio(request: TextRequest):
#     try:
#         if not client:
#             raise HTTPException(status_code=500, detail="Murf API key not configured")
            
#         audio_res = client.text_to_speech.generate(
#             text=request.text,
#             voice_id="en-US-terrell"
#         )
#         return {"audio_url": audio_res.audio_file}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Upload audio endpoint
# @app.post("/upload-audio/")
# async def upload_audio(file: UploadFile = File(...)):
#     timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#     unique_id = uuid.uuid4().hex[:6]
#     extension = file.filename.split(".")[-1] if "." in file.filename else "webm"
#     new_filename = f"audio_{timestamp}_{unique_id}.{extension}"

#     file_path = UPLOAD_DIR / new_filename
#     contents = await file.read()

#     with open(file_path, "wb") as f:
#         f.write(contents)

#     return {
#         "filename": new_filename,
#         "content_type": file.content_type,
#         "size": len(contents),
#         "file_path": str(file_path)
#     }

# # Transcribe file endpoint using AssemblyAI SDK
# @app.post("/transcribe/file")
# async def transcribe_file(file: UploadFile = File(...)):
#     try:
#         # Read contents of the uploaded file
#         audio_bytes = await file.read()

#         # Use AssemblyAI SDK to transcribe directly from bytes
#         transcriber = aai.Transcriber()
#         transcript = transcriber.transcribe(audio_bytes)

#         if transcript.status == aai.TranscriptStatus.error:
#             raise RuntimeError(f"Transcription failed: {transcript.error}")

#         return {"transcript": transcript.text}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Main echo endpoint - FIXED VERSION
# @app.post("/tts/echo")
# async def tts_echo(
#     audio_file: UploadFile = File(...), 
#     voiceId: Optional[str] = Form(default="en-US-natalie")
# ):
#     """
#     Echo endpoint that:
#     1. Accepts audio file and optional voice ID
#     2. Transcribes using AssemblyAI SDK
#     3. Generates TTS using Murf SDK with selected voice
#     4. Returns audio URL
#     """
#     try:
#         print(f"Processing audio file: {audio_file.filename}")
#         print(f"Selected voice: {voiceId}")
        
#         # Step 1: Read audio file
#         audio_bytes = await audio_file.read()
#         print(f"Audio file size: {len(audio_bytes)} bytes")
        
#         # Step 2: Transcribe audio using AssemblyAI SDK
#         print("Starting transcription with AssemblyAI...")
#         transcriber = aai.Transcriber()
#         transcript = transcriber.transcribe(audio_bytes)
        
#         if transcript.status == aai.TranscriptStatus.error:
#             raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
        
#         transcribed_text = transcript.text
#         print(f"Transcription completed: {transcribed_text}")
        
#         if not transcribed_text or transcribed_text.strip() == "":
#             return JSONResponse(
#                 status_code=400, 
#                 content={"error": "No speech detected in audio"}
#             )
        
#         # Step 3: Generate TTS using Murf SDK with selected voice
#         print(f"Generating TTS with Murf using voice: {voiceId}")
#         if not client:
#             raise HTTPException(status_code=500, detail="Murf API key not configured")
        
#         try:
#             # Use Murf SDK for TTS generation with selected voice
#             audio_res = client.text_to_speech.generate(
#                 text=transcribed_text,
#                 voice_id=voiceId  # Use the selected voice
#             )
            
#             audio_url = audio_res.audio_file
#             print(f"TTS generation completed: {audio_url}")
            
#             return {
#                 "text": transcribed_text,
#                 "audio_url": audio_url,
#                 "voice_id": voiceId,
#                 "status": "success"
#             }
            
#         except Exception as murf_error:
#             print(f"Murf SDK error: {str(murf_error)}")
#             # Fallback to direct API call if SDK fails
#             return await generate_murf_tts_fallback(transcribed_text, voiceId)
        
#     except Exception as e:
#         print(f"Error in tts_echo: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# async def generate_murf_tts_fallback(text: str, voice_id: str = "en-US-natalie") -> Dict[str, Any]:
#     """
#     Fallback method using direct Murf API calls with voice selection
#     """
#     try:
#         print(f"Using Murf API fallback method with voice: {voice_id}")
        
#         # Murf API direct call
#         headers = {
#             "Authorization": f"Bearer {MURF_API_KEY}",
#             "Content-Type": "application/json"
#         }
        
#         payload = {
#             "voiceId": voice_id,  # Use the selected voice
#             "style": "Conversational",
#             "text": text,
#             "rate": 0,
#             "pitch": 0,
#             "sampleRate": 22050,
#             "format": "MP3",
#             "channelType": "MONO",
#             "pronunciationDictionary": {},
#             "encodeAsBase64": False
#         }
        
#         response = requests.post(
#             "https://api.murf.ai/v1/speech/generate",
#             headers=headers,
#             json=payload,
#             timeout=30
#         )
        
#         if response.status_code != 200:
#             print(f"Murf API error: {response.status_code} - {response.text}")
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=f"Murf API error: {response.text}"
#             )
        
#         result = response.json()
        
#         if "audioFile" not in result:
#             raise HTTPException(
#                 status_code=500,
#                 detail="Invalid response from Murf API - no audio file"
#             )
        
#         return {
#             "text": text,
#             "audio_url": result["audioFile"],
#             "voice_id": voice_id,
#             "status": "success"
#         }
        
#     except requests.exceptions.RequestException as e:
#         print(f"Request error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Request to Murf API failed: {str(e)}")
#     except Exception as e:
#         print(f"Fallback TTS generation error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

# # Get available voices from Murf
# @app.get("/voices")
# async def get_available_voices():
#     """
#     Get available voices from Murf API
#     """
#     try:
#         if not client:
#             raise HTTPException(status_code=500, detail="Murf API key not configured")
            
#         # Try to use SDK method first
#         try:
#             voices = client.voices.list()
#             return {"voices": voices}
#         except:
#             # Fallback to direct API call
#             headers = {"Authorization": f"Bearer {MURF_API_KEY}"}
#             response = requests.get(
#                 "https://api.murf.ai/v1/speech/voices",
#                 headers=headers,
#                 timeout=10
#             )
            
#             if response.status_code != 200:
#                 raise HTTPException(
#                     status_code=response.status_code,
#                     detail=f"Failed to fetch voices: {response.text}"
#                 )
            
#             return response.json()
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")

# # Health check endpoint - UPDATED to include Gemini status and chat history info
# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "assemblyai_configured": bool(ASSEMBLYAI_API_KEY),
#         "murf_configured": bool(MURF_API_KEY and client),
#         "murf_sdk_available": client is not None,
#         "gemini_configured": bool(GEMINI_API_KEY and gemini_model),
#         "gemini_model": "gemini-1.5-flash" if gemini_model else None,
#         "chat_sessions_active": len(CHAT_HISTORY),
#         "total_messages": sum(len(history) for history in CHAT_HISTORY.values())
#     }

# async def generate_murf_audio(text: str, voice_id: str = "en-US-natalie") -> str:
#     """
#     Generate audio using Murf API for given text
#     Returns the audio URL
#     """
#     try:
#         if not client:
#             # Fallback to direct API call
#             headers = {
#                 "Authorization": f"Bearer {MURF_API_KEY}",
#                 "Content-Type": "application/json"
#             }
            
#             payload = {
#                 "voiceId": voice_id,
#                 "style": "Conversational",
#                 "text": text,
#                 "rate": 0,
#                 "pitch": 0,
#                 "sampleRate": 22050,
#                 "format": "MP3",
#                 "channelType": "MONO",
#                 "pronunciationDictionary": {},
#                 "encodeAsBase64": False
#             }
            
#             response = requests.post(
#                 "https://api.murf.ai/v1/speech/generate",
#                 headers=headers,
#                 json=payload,
#                 timeout=30
#             )
            
#             if response.status_code != 200:
#                 raise HTTPException(
#                     status_code=response.status_code,
#                     detail=f"Murf API error: {response.text}"
#                 )
            
#             result = response.json()
#             return result["audioFile"]
        
#         else:
#             # Use Murf SDK
#             audio_res = client.text_to_speech.generate(
#                 text=text,
#                 voice_id=voice_id
#             )
#             return audio_res.audio_file
            
#     except Exception as e:
#         print(f"Murf audio generation error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

# # Helper function to split text for Murf's character limit
# def split_text_for_murf(text: str, max_chars: int = 2800) -> list:
#     """
#     Split text into chunks that fit within Murf's character limit
#     Tries to split at sentence boundaries when possible
#     """
#     if len(text) <= max_chars:
#         return [text]
    
#     chunks = []
#     current_chunk = ""
    
#     # Split by sentences first
#     sentences = text.replace('!', '.').replace('?', '.').split('.')
    
#     for sentence in sentences:
#         sentence = sentence.strip()
#         if not sentence:
#             continue
            
#         sentence += "."  # Add period back
        
#         # If adding this sentence exceeds limit, save current chunk and start new one
#         if len(current_chunk + sentence) > max_chars:
#             if current_chunk:
#                 chunks.append(current_chunk.strip())
#                 current_chunk = sentence
#             else:
#                 # Single sentence is too long, force split by words
#                 words = sentence.split()
#                 temp_chunk = ""
#                 for word in words:
#                     if len(temp_chunk + " " + word) > max_chars:
#                         if temp_chunk:
#                             chunks.append(temp_chunk.strip())
#                             temp_chunk = word
#                         else:
#                             # Single word too long, force character split
#                             chunks.append(word[:max_chars])
#                             temp_chunk = word[max_chars:]
#                     else:
#                         temp_chunk += " " + word if temp_chunk else word
                
#                 if temp_chunk:
#                     current_chunk = temp_chunk
#         else:
#             current_chunk += " " + sentence if current_chunk else sentence
    
#     # Add the last chunk
#     if current_chunk:
#         chunks.append(current_chunk.strip())
    
#     return chunks

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)



from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from murf import Murf
from dotenv import load_dotenv
from pathlib import Path as PathLib
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
import logging
import traceback
from functools import wraps
import asyncio

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Robust Echo Bot v2 with Comprehensive Error Handling")

# Mount static files (HTML, JS, etc.)
static_dir = PathLib("static")
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

# Configuration - Get from environment variables with fallback error messages
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY") 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# UNCOMMENT THESE LINES TO SIMULATE API FAILURES:
#ASSEMBLYAI_API_KEY = None  # Simulate STT failure
# MURF_API_KEY = None        # Simulate TTS failure  
# GEMINI_API_KEY = None      # Simulate LLM failure

# Error messages for different failure scenarios
ERROR_MESSAGES = {
    "stt_failure": "I'm having trouble understanding your audio right now. Please try again or type your message instead.",
    "llm_failure": "I'm having trouble connecting to my brain right now. Let me try that again.",
    "tts_failure": "I can understand you, but I'm having trouble speaking right now. Here's my text response instead.",
    "general_failure": "I'm experiencing some technical difficulties. Please try again in a moment.",
    "no_input": "I didn't catch that. Could you please try recording again or type your message?",
    "timeout": "That took longer than expected. Let me try a different approach.",
    "network_error": "I'm having trouble connecting right now. Please check your internet connection and try again."
}

# Fallback TTS audio URLs (pre-generated error messages)
FALLBACK_AUDIO_URLS = {
    "stt_failure": "https://example.com/fallback/stt_error.mp3",
    "llm_failure": "https://example.com/fallback/llm_error.mp3", 
    "tts_failure": "https://example.com/fallback/tts_error.mp3",
    "general_failure": "https://example.com/fallback/general_error.mp3"
}

# ENHANCED: In-memory chat history storage
CHAT_HISTORY: Dict[str, List[Dict]] = {}

# Error handling decorators
def handle_api_errors(error_type: str):
    """Decorator to handle specific API errors with fallback responses"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{error_type} error in {func.__name__}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                error_response = {
                    "error": True,
                    "error_type": error_type,
                    "error_message": ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["general_failure"]),
                    "fallback_audio_url": FALLBACK_AUDIO_URLS.get(error_type),
                    "status": "error",
                    "original_error": str(e)
                }
                
                return error_response
        return wrapper
    return decorator

def retry_with_fallback(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry operations with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempt {attempt + 1}/{max_retries} for {func.__name__}")
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator

# Enhanced API client initialization with error handling
def initialize_apis():
    """Initialize all API clients with proper error handling"""
    api_status = {
        "assemblyai": False,
        "murf": False,
        "gemini": False,
        "errors": []
    }
    
    # Initialize AssemblyAI
    try:
        if ASSEMBLYAI_API_KEY:
            aai.settings.api_key = ASSEMBLYAI_API_KEY
            api_status["assemblyai"] = True
            logger.info("AssemblyAI initialized successfully")
        else:
            api_status["errors"].append("AssemblyAI API key not configured")
            logger.error("AssemblyAI API key missing")
    except Exception as e:
        api_status["errors"].append(f"AssemblyAI initialization failed: {str(e)}")
        logger.error(f"AssemblyAI initialization error: {str(e)}")
    
    # Initialize Murf
    try:
        if MURF_API_KEY:
            global client
            client = Murf(api_key=MURF_API_KEY)
            api_status["murf"] = True
            logger.info("Murf initialized successfully")
        else:
            client = None
            api_status["errors"].append("Murf API key not configured")
            logger.error("Murf API key missing")
    except Exception as e:
        client = None
        api_status["errors"].append(f"Murf initialization failed: {str(e)}")
        logger.error(f"Murf initialization error: {str(e)}")
    
    # Initialize Gemini
    try:
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            global gemini_model
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            api_status["gemini"] = True
            logger.info("Gemini initialized successfully")
        else:
            gemini_model = None
            api_status["errors"].append("Gemini API key not configured")
            logger.error("Gemini API key missing")
    except Exception as e:
        gemini_model = None
        api_status["errors"].append(f"Gemini initialization failed: {str(e)}")
        logger.error(f"Gemini initialization error: {str(e)}")
    
    return api_status

# Initialize APIs on startup
api_status = initialize_apis()

# Enhanced utility functions with error handling
def get_chat_history(session_id: str) -> List[Dict]:
    """Get chat history for a session with error handling"""
    try:
        return CHAT_HISTORY.get(session_id, [])
    except Exception as e:
        logger.error(f"Error retrieving chat history for session {session_id}: {str(e)}")
        return []

def add_to_chat_history(session_id: str, role: str, content: str):
    """Add a message to chat history with error handling"""
    try:
        if session_id not in CHAT_HISTORY:
            CHAT_HISTORY[session_id] = []
        
        CHAT_HISTORY[session_id].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        logger.info(f"Added {role} message to session {session_id}")
    except Exception as e:
        logger.error(f"Error adding message to chat history: {str(e)}")

def format_chat_for_gemini(session_id: str, new_user_message: str) -> str:
    """Format chat history for Gemini API with error handling"""
    try:
        history = get_chat_history(session_id)
        
        # Build conversation context
        conversation = []
        for msg in history[-10:]:  # Keep last 10 messages for context
            if msg["role"] == "user":
                conversation.append(f"User: {msg['content']}")
            else:
                conversation.append(f"Assistant: {msg['content']}")
        
        # Add new user message
        conversation.append(f"User: {new_user_message}")
        
        # Create prompt with context
        if len(conversation) == 1:
            # First message in conversation
            prompt = f"You are a helpful AI assistant. Please respond conversationally (maximum 2500 characters) to: {new_user_message}"
        else:
            # Continuing conversation
            context = "\n".join(conversation[:-1])
            prompt = f"""You are a helpful AI assistant. Here's our conversation so far:

{context}

Now the user says: {new_user_message}

Please respond naturally and conversationally (maximum 2500 characters):"""
        
        return prompt
    except Exception as e:
        logger.error(f"Error formatting chat for Gemini: {str(e)}")
        return f"Please respond to: {new_user_message}"

# STT function with error handling
@handle_api_errors("stt_failure")
@retry_with_fallback(max_retries=2)
async def transcribe_audio_with_fallback(audio_bytes: bytes) -> str:
    """Transcribe audio with comprehensive error handling"""
    if not ASSEMBLYAI_API_KEY:
        raise ValueError("AssemblyAI API key not configured")
    
    try:
        logger.info(f"Starting transcription for {len(audio_bytes)} bytes")
        transcriber = aai.Transcriber()
        
        # Add timeout handling
        transcript = transcriber.transcribe(audio_bytes)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise ValueError(f"Transcription failed: {transcript.error}")
        
        if not transcript.text or transcript.text.strip() == "":
            raise ValueError("No speech detected in audio")
            
        logger.info(f"Transcription successful: {len(transcript.text)} characters")
        return transcript.text.strip()
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise

#LLM function with error handling
@handle_api_errors("llm_failure")
@retry_with_fallback(max_retries=2)
async def generate_llm_response_with_fallback(session_id: str, user_input: str) -> str:
    """Generate LLM response with comprehensive error handling"""
    if not gemini_model:
        raise ValueError("Gemini API key not configured")
    
    try:
        formatted_prompt = format_chat_for_gemini(session_id, user_input)
        logger.info(f"Querying Gemini for session {session_id}")
        
        response = gemini_model.generate_content(formatted_prompt)
        
        if not response.text:
            raise ValueError("No response generated from Gemini")
        
        llm_response = response.text.strip()
        logger.info(f"Gemini response generated: {len(llm_response)} characters")
        
        return llm_response
        
    except Exception as e:
        logger.error(f"LLM generation error: {str(e)}")
        raise

# Enhanced TTS function with error handling
@handle_api_errors("tts_failure") 
@retry_with_fallback(max_retries=2)
async def generate_audio_with_fallback(text: str, voice_id: str = "en-US-natalie") -> str:
    """Generate TTS audio with comprehensive error handling"""
    if not MURF_API_KEY:
        raise ValueError("Murf API key not configured")
    
    try:
        logger.info(f"Generating TTS for {len(text)} characters with voice {voice_id}")
        
        if client:
            # Use Murf SDK
            audio_res = client.text_to_speech.generate(
                text=text,
                voice_id=voice_id
            )
            return audio_res.audio_file
        else:
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
            
            async with httpx.AsyncClient(timeout=30.0) as client_http:
                response = await client_http.post(
                    "https://api.murf.ai/v1/speech/generate",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    raise ValueError(f"Murf API error: {response.status_code} - {response.text}")
                
                result = response.json()
                return result["audioFile"]
                
    except Exception as e:
        logger.error(f"TTS generation error: {str(e)}")
        raise

# Create upload directory
UPLOAD_DIR = PathLib("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic models
class TextRequest(BaseModel):
    text: str

class LLMQueryRequest(BaseModel):
    text: str

# ENHANCED MAIN CHAT ENDPOINT with comprehensive error handling
@app.post("/agent/chat/{session_id}")
async def agent_chat(
    session_id: str = Path(..., description="Session ID for chat history"),
    audio_file: UploadFile = File(None),
    text: Optional[str] = Form(None),
    voiceId: Optional[str] = Form(default="en-US-natalie")
):
    """
    Enhanced Chat endpoint with comprehensive error handling and fallback responses
    """
    logger.info(f"[Session {session_id}] Starting chat request")
    
    try:
        input_text = ""
        transcription_error = False
        llm_error = False
        tts_error = False
        
        # Step 1: Get input text (from audio or direct text) with error handling
        if audio_file:
            logger.info(f"[Session {session_id}] Processing audio input: {audio_file.filename}")
            
            try:
                audio_bytes = await audio_file.read()
                logger.info(f"[Session {session_id}] Audio file size: {len(audio_bytes)} bytes")
                
                # Attempt transcription with fallback
                transcription_result = await transcribe_audio_with_fallback(audio_bytes)
                
                if isinstance(transcription_result, dict) and transcription_result.get("error"):
                    # STT failed - return error response with fallback
                    transcription_error = True
                    return JSONResponse(
                        status_code=200,  # Don't return 500, let client handle gracefully
                        content={
                            "session_id": session_id,
                            "error": True,
                            "error_type": "stt_failure", 
                            "error_message": transcription_result["error_message"],
                            "fallback_audio_url": transcription_result.get("fallback_audio_url"),
                            "suggestion": "Please try recording again or type your message instead.",
                            "status": "error"
                        }
                    )
                
                input_text = transcription_result
                logger.info(f"[Session {session_id}] Transcribed text: {input_text}")
                
            except Exception as e:
                logger.error(f"[Session {session_id}] Audio processing failed: {str(e)}")
                return JSONResponse(
                    status_code=200,
                    content={
                        "session_id": session_id,
                        "error": True,
                        "error_type": "stt_failure",
                        "error_message": ERROR_MESSAGES["stt_failure"],
                        "fallback_audio_url": FALLBACK_AUDIO_URLS.get("stt_failure"),
                        "suggestion": "Please try recording again or type your message instead.",
                        "status": "error"
                    }
                )
            
        elif text:
            input_text = text.strip()
            logger.info(f"[Session {session_id}] Direct text input: {input_text}")
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "session_id": session_id,
                    "error": True,
                    "error_type": "no_input",
                    "error_message": ERROR_MESSAGES["no_input"],
                    "status": "error"
                }
            )
        
        if not input_text:
            return JSONResponse(
                status_code=400,
                content={
                    "session_id": session_id,
                    "error": True,
                    "error_type": "no_input",
                    "error_message": ERROR_MESSAGES["no_input"],
                    "status": "error"
                }
            )
        
        # Step 2: Add user message to chat history
        add_to_chat_history(session_id, "user", input_text)
        logger.info(f"[Session {session_id}] Added user message to history")
        
        # Step 3: Generate LLM response with error handling
        try:
            llm_response_result = await generate_llm_response_with_fallback(session_id, input_text)
            
            if isinstance(llm_response_result, dict) and llm_response_result.get("error"):
                # LLM failed - return error response with text-only fallback
                llm_error = True
                fallback_response = f"I'm having trouble processing that right now. You said: '{input_text}'. Could you please try rephrasing your question?"
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "session_id": session_id,
                        "input": input_text,
                        "response": fallback_response,
                        "error": True,
                        "error_type": "llm_failure",
                        "error_message": llm_response_result["error_message"],
                        "fallback_audio_url": llm_response_result.get("fallback_audio_url"),
                        "status": "error_with_fallback"
                    }
                )
            
            llm_response = llm_response_result
            logger.info(f"[Session {session_id}] LLM response generated: {len(llm_response)} characters")
            
        except Exception as e:
            logger.error(f"[Session {session_id}] LLM processing failed: {str(e)}")
            fallback_response = f"I'm having trouble processing that right now. You said: '{input_text}'. Could you please try rephrasing your question?"
            
            return JSONResponse(
                status_code=200,
                content={
                    "session_id": session_id,
                    "input": input_text,
                    "response": fallback_response,
                    "error": True,
                    "error_type": "llm_failure",
                    "error_message": ERROR_MESSAGES["llm_failure"],
                    "fallback_audio_url": FALLBACK_AUDIO_URLS.get("llm_failure"),
                    "status": "error_with_fallback"
                }
            )
        
        # Step 4: Add assistant response to chat history
        add_to_chat_history(session_id, "assistant", llm_response)
        logger.info(f"[Session {session_id}] Added assistant response to history")
        
        # Step 5: Generate TTS with error handling
        audio_urls = []
        try:
            if len(llm_response) <= 3000:
                # Single request
                audio_result = await generate_audio_with_fallback(llm_response, voiceId)
                
                if isinstance(audio_result, dict) and audio_result.get("error"):
                    # TTS failed but we have text response
                    tts_error = True
                    logger.warning(f"[Session {session_id}] TTS failed, returning text-only response")
                else:
                    audio_urls.append(audio_result)
            else:
                # Split into chunks
                chunks = split_text_for_murf(llm_response, 2800)
                logger.info(f"[Session {session_id}] Split response into {len(chunks)} chunks")
                
                for i, chunk in enumerate(chunks):
                    logger.info(f"[Session {session_id}] Processing chunk {i+1}/{len(chunks)}")
                    try:
                        audio_result = await generate_audio_with_fallback(chunk, voiceId)
                        if isinstance(audio_result, dict) and audio_result.get("error"):
                            tts_error = True
                            break
                        audio_urls.append(audio_result)
                    except Exception as chunk_error:
                        logger.error(f"[Session {session_id}] Chunk {i+1} TTS failed: {str(chunk_error)}")
                        tts_error = True
                        break
                        
        except Exception as e:
            logger.error(f"[Session {session_id}] TTS generation failed: {str(e)}")
            tts_error = True
        
        # Step 6: Prepare response
        history = get_chat_history(session_id)
        conversation_length = len(history)
        
        response_data = {
            "session_id": session_id,
            "input": input_text,
            "response": llm_response,
            "model": "gemini-1.5-flash",
            "voice_id": voiceId,
            "audio_urls": audio_urls,
            "audio_url": audio_urls[0] if audio_urls else None,
            "chunks_count": len(audio_urls),
            "conversation_length": conversation_length,
            "conversation_turns": conversation_length // 2,
            "status": "success"
        }
        
        # Add TTS error info if applicable
        if tts_error:
            response_data.update({
                "tts_error": True,
                "tts_error_message": ERROR_MESSAGES["tts_failure"],
                "fallback_audio_url": FALLBACK_AUDIO_URLS.get("tts_failure"),
                "status": "success_no_audio"
            })
        
        return response_data
        
    except Exception as e:
        logger.error(f"[Session {session_id}] Unexpected error in agent_chat: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=200,  # Return 200 to allow client to handle gracefully
            content={
                "session_id": session_id,
                "error": True,
                "error_type": "general_failure",
                "error_message": ERROR_MESSAGES["general_failure"],
                "fallback_audio_url": FALLBACK_AUDIO_URLS.get("general_failure"),
                "original_error": str(e),
                "status": "error"
            }
        )

# Get conversation history endpoint with error handling
@app.get("/agent/history/{session_id}")
async def get_conversation_history(session_id: str = Path(..., description="Session ID")):
    """Get conversation history with error handling"""
    try:
        history = get_chat_history(session_id)
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "conversation_turns": len(history) // 2,
            "history": history,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving history for session {session_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "error_message": f"Failed to retrieve history: {str(e)}",
                "status": "error"
            }
        )

# Clear conversation history with error handling
@app.delete("/agent/history/{session_id}")
async def clear_conversation_history(session_id: str = Path(..., description="Session ID")):
    """Clear conversation history with error handling"""
    try:
        if session_id in CHAT_HISTORY:
            del CHAT_HISTORY[session_id]
            return {
                "session_id": session_id,
                "message": "Conversation history cleared",
                "status": "success"
            }
        else:
            return {
                "session_id": session_id,
                "message": "No history found for this session",
                "status": "success"
            }
        
    except Exception as e:
        logger.error(f"Error clearing history for session {session_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "error_message": f"Failed to clear history: {str(e)}",
                "status": "error"
            }
        )

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check with detailed API status"""
    try:
        health_status = {
            "status": "healthy" if all([
                api_status["assemblyai"], 
                api_status["murf"], 
                api_status["gemini"]
            ]) else "degraded",
            "timestamp": datetime.now().isoformat(),
            "apis": {
                "assemblyai": {
                    "configured": bool(ASSEMBLYAI_API_KEY),
                    "status": "healthy" if api_status["assemblyai"] else "unavailable"
                },
                "murf": {
                    "configured": bool(MURF_API_KEY),
                    "sdk_available": client is not None,
                    "status": "healthy" if api_status["murf"] else "unavailable"
                },
                "gemini": {
                    "configured": bool(GEMINI_API_KEY),
                    "model": "gemini-1.5-flash" if gemini_model else None,
                    "status": "healthy" if api_status["gemini"] else "unavailable"
                }
            },
            "chat_sessions": {
                "active_sessions": len(CHAT_HISTORY),
                "total_messages": sum(len(history) for history in CHAT_HISTORY.values())
            },
            "errors": api_status.get("errors", [])
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Enhanced error simulation endpoint for testing
@app.post("/simulate-error/{error_type}")
async def simulate_error(error_type: str):
    """Simulate different types of errors for testing"""
    try:
        if error_type == "stt":
            global ASSEMBLYAI_API_KEY
            ASSEMBLYAI_API_KEY = None
            return {"message": "STT error simulated - AssemblyAI API key removed"}
        elif error_type == "llm":
            global GEMINI_API_KEY, gemini_model
            GEMINI_API_KEY = None
            gemini_model = None
            return {"message": "LLM error simulated - Gemini API key removed"}
        elif error_type == "tts":
            global MURF_API_KEY, client
            MURF_API_KEY = None
            client = None
            return {"message": "TTS error simulated - Murf API key removed"}
        elif error_type == "reset":
            # Reset APIs to original state
            initialize_apis()
            return {"message": "APIs reset to original configuration"}
        else:
            return {"error": "Invalid error type. Use: stt, llm, tts, or reset"}
            
    except Exception as e:
        return {"error": f"Failed to simulate error: {str(e)}"}

# Helper function to split text for Murf's character limit
def split_text_for_murf(text: str, max_chars: int = 2800) -> list:
    """Split text into chunks that fit within Murf's character limit with error handling"""
    try:
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
        
        return chunks if chunks else [text]  # Fallback to original text if splitting fails
        
    except Exception as e:
        logger.error(f"Error splitting text: {str(e)}")
        return [text]  # Return original text as single chunk on error

# Legacy endpoints with enhanced error handling

@app.post("/generate-audio/")
async def generate_audio(request: TextRequest):
    """Legacy endpoint for direct text-to-speech with error handling"""
    try:
        if not client and not MURF_API_KEY:
            return JSONResponse(
                status_code=200,
                content={
                    "error": True,
                    "error_message": ERROR_MESSAGES["tts_failure"],
                    "fallback_audio_url": FALLBACK_AUDIO_URLS.get("tts_failure")
                }
            )
            
        audio_url = await generate_audio_with_fallback(request.text, "en-US-terrell")
        
        if isinstance(audio_url, dict) and audio_url.get("error"):
            return JSONResponse(
                status_code=200,
                content=audio_url
            )
            
        return {"audio_url": audio_url, "status": "success"}
        
    except Exception as e:
        logger.error(f"Legacy generate_audio error: {str(e)}")
        return JSONResponse(
            status_code=200,
            content={
                "error": True,
                "error_message": ERROR_MESSAGES["tts_failure"],
                "original_error": str(e)
            }
        )

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    """Upload audio endpoint with error handling"""
    try:
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
            "file_path": str(file_path),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "error_message": f"File upload failed: {str(e)}"
            }
        )

@app.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...)):
    """Transcribe file endpoint with error handling"""
    try:
        audio_bytes = await file.read()
        
        transcription_result = await transcribe_audio_with_fallback(audio_bytes)
        
        if isinstance(transcription_result, dict) and transcription_result.get("error"):
            return JSONResponse(
                status_code=200,
                content=transcription_result
            )

        return {
            "transcript": transcription_result,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"File transcription error: {str(e)}")
        return JSONResponse(
            status_code=200,
            content={
                "error": True,
                "error_type": "stt_failure",
                "error_message": ERROR_MESSAGES["stt_failure"],
                "original_error": str(e)
            }
        )

@app.post("/tts/echo")
async def tts_echo(
    audio_file: UploadFile = File(...), 
    voiceId: Optional[str] = Form(default="en-US-natalie")
):
    """Enhanced echo endpoint with comprehensive error handling"""
    try:
        logger.info(f"Processing echo request with voice: {voiceId}")
        
        # Step 1: Read and transcribe audio
        audio_bytes = await audio_file.read()
        logger.info(f"Audio file size: {len(audio_bytes)} bytes")
        
        transcription_result = await transcribe_audio_with_fallback(audio_bytes)
        
        if isinstance(transcription_result, dict) and transcription_result.get("error"):
            return JSONResponse(
                status_code=200,
                content=transcription_result
            )
        
        transcribed_text = transcription_result
        logger.info(f"Transcription completed: {transcribed_text}")
        
        if not transcribed_text or transcribed_text.strip() == "":
            return JSONResponse(
                status_code=200,
                content={
                    "error": True,
                    "error_type": "no_input",
                    "error_message": ERROR_MESSAGES["no_input"]
                }
            )
        
        # Step 2: Generate TTS
        audio_result = await generate_audio_with_fallback(transcribed_text, voiceId)
        
        if isinstance(audio_result, dict) and audio_result.get("error"):
            # TTS failed, return text-only response
            return JSONResponse(
                status_code=200,
                content={
                    "text": transcribed_text,
                    "voice_id": voiceId,
                    "error": True,
                    "error_type": "tts_failure",
                    "error_message": audio_result["error_message"],
                    "fallback_audio_url": audio_result.get("fallback_audio_url"),
                    "status": "success_no_audio"
                }
            )
        
        return {
            "text": transcribed_text,
            "audio_url": audio_result,
            "voice_id": voiceId,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Echo endpoint error: {str(e)}")
        return JSONResponse(
            status_code=200,
            content={
                "error": True,
                "error_type": "general_failure",
                "error_message": ERROR_MESSAGES["general_failure"],
                "original_error": str(e)
            }
        )

@app.post("/llm/query")
async def llm_query(
    audio_file: UploadFile = File(None),
    text: Optional[str] = Form(None),
    voiceId: Optional[str] = Form(default="en-US-natalie")
):
    """Enhanced LLM Query endpoint with comprehensive error handling"""
    try:
        logger.info("Processing LLM query request")
        
        input_text = ""
        
        # Step 1: Get input text
        if audio_file:
            logger.info(f"Processing audio input: {audio_file.filename}")
            
            audio_bytes = await audio_file.read()
            logger.info(f"Audio file size: {len(audio_bytes)} bytes")
            
            transcription_result = await transcribe_audio_with_fallback(audio_bytes)
            
            if isinstance(transcription_result, dict) and transcription_result.get("error"):
                return JSONResponse(
                    status_code=200,
                    content=transcription_result
                )
            
            input_text = transcription_result
            logger.info(f"Transcribed text: {input_text}")
            
        elif text:
            input_text = text.strip()
            logger.info(f"Direct text input: {input_text}")
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "error_type": "no_input",
                    "error_message": ERROR_MESSAGES["no_input"]
                }
            )
        
        if not input_text:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "error_type": "no_input",
                    "error_message": ERROR_MESSAGES["no_input"]
                }
            )
        
        # Step 2: Generate LLM response
        prompt = f"Please provide a conversational response (maximum 2500 characters) to: {input_text}"
        
        try:
            if not gemini_model:
                raise ValueError("Gemini API key not configured")
                
            response = gemini_model.generate_content(prompt)
            
            if not response.text:
                raise ValueError("No response generated from Gemini")
            
            llm_response = response.text.strip()
            logger.info(f"Gemini response length: {len(llm_response)} chars")
            
        except Exception as llm_error:
            logger.error(f"LLM processing failed: {str(llm_error)}")
            fallback_response = f"I'm having trouble processing that right now. You said: '{input_text}'. Could you please try rephrasing your question?"
            
            return JSONResponse(
                status_code=200,
                content={
                    "input": input_text,
                    "response": fallback_response,
                    "error": True,
                    "error_type": "llm_failure",
                    "error_message": ERROR_MESSAGES["llm_failure"],
                    "fallback_audio_url": FALLBACK_AUDIO_URLS.get("llm_failure"),
                    "status": "error_with_fallback"
                }
            )
        
        # Step 3: Generate TTS with error handling
        audio_urls = []
        tts_error = False
        
        try:
            if len(llm_response) <= 3000:
                # Single request
                audio_result = await generate_audio_with_fallback(llm_response, voiceId)
                
                if isinstance(audio_result, dict) and audio_result.get("error"):
                    tts_error = True
                else:
                    audio_urls.append(audio_result)
            else:
                # Split into chunks
                chunks = split_text_for_murf(llm_response, 2800)
                logger.info(f"Split response into {len(chunks)} chunks")
                
                for i, chunk in enumerate(chunks):
                    logger.info(f"Processing chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
                    try:
                        audio_result = await generate_audio_with_fallback(chunk, voiceId)
                        if isinstance(audio_result, dict) and audio_result.get("error"):
                            tts_error = True
                            break
                        audio_urls.append(audio_result)
                    except Exception as chunk_error:
                        logger.error(f"Chunk {i+1} TTS failed: {str(chunk_error)}")
                        tts_error = True
                        break
                        
        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}")
            tts_error = True
        
        response_data = {
            "input": input_text,
            "response": llm_response,
            "model": "gemini-1.5-flash",
            "voice_id": voiceId,
            "audio_urls": audio_urls,
            "audio_url": audio_urls[0] if audio_urls else None,
            "chunks_count": len(audio_urls),
            "status": "success" if not tts_error else "success_no_audio"
        }
        
        if tts_error:
            response_data.update({
                "tts_error": True,
                "tts_error_message": ERROR_MESSAGES["tts_failure"],
                "fallback_audio_url": FALLBACK_AUDIO_URLS.get("tts_failure")
            })
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in llm_query: {str(e)}")
        return JSONResponse(
            status_code=200,
            content={
                "error": True,
                "error_type": "general_failure", 
                "error_message": ERROR_MESSAGES["general_failure"],
                "original_error": str(e)
            }
        )

@app.get("/voices")
async def get_available_voices():
    """Get available voices with error handling"""
    try:
        if not client and not MURF_API_KEY:
            return JSONResponse(
                status_code=200,
                content={
                    "error": True,
                    "error_message": "Murf API key not configured",
                    "voices": []
                }
            )
            
        # Try to use SDK method first
        try:
            if client:
                voices = client.voices.list()
                return {"voices": voices, "status": "success"}
        except Exception as sdk_error:
            logger.warning(f"Murf SDK voices list failed: {str(sdk_error)}")
            
        # Fallback to direct API call
        headers = {"Authorization": f"Bearer {MURF_API_KEY}"}
        
        async with httpx.AsyncClient(timeout=10.0) as client_http:
            response = await client_http.get(
                "https://api.murf.ai/v1/speech/voices",
                headers=headers
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch voices: {response.text}")
            
            result = response.json()
            result["status"] = "success"
            return result
        
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        return JSONResponse(
            status_code=200,
            content={
                "error": True,
                "error_message": f"Error fetching voices: {str(e)}",
                "voices": []
            }
        )

@app.get("/agent/sessions")
async def list_active_sessions():
    """List all active sessions with error handling"""
    try:
        sessions_info = []
        for session_id, history in CHAT_HISTORY.items():
            if history:  # Only include sessions with messages
                sessions_info.append({
                    "session_id": session_id,
                    "message_count": len(history),
                    "conversation_turns": len(history) // 2,
                    "last_message_time": history[-1]["timestamp"] if history else None,
                    "created_time": history[0]["timestamp"] if history else None
                })
        
        return {
            "active_sessions": len(sessions_info),
            "sessions": sessions_info,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "error_message": f"Failed to list sessions: {str(e)}"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)