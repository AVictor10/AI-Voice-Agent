# from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Path
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from murf import Murf
# from dotenv import load_dotenv
# from pathlib import Path as PathLib
# from datetime import datetime
# from typing import Dict, List, Optional, Any
# import time
# import assemblyai as aai
# import os
# import uuid
# import tempfile
# import requests
# import json
# from fastapi import Body
# import httpx
# import google.generativeai as genai
# import logging
# import traceback
# from functools import wraps
# import asyncio
# import websockets
# import base64
# import wave
# import struct
# from collections import deque

# # Initialize global variables at module level
# client = None
# gemini_model = None
# websocket_pool = {}

# # Configure comprehensive logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# load_dotenv()

# app = FastAPI(title="AI Voice Agent")

# # Mount static files (HTML, JS, etc.)
# static_dir = PathLib("static")
# static_dir.mkdir(exist_ok=True)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/")
# async def root():
#     return FileResponse("static/index.html")

# # Enhanced CORS middleware configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
#     expose_headers=["*"],
#     max_age=3600,
# )

# # Configuration - Get from environment variables
# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# MURF_API_KEY = os.getenv("MURF_API_KEY") 
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # ============================================================================
# # ENHANCED MURF WEBSOCKET STREAMING CLASS
# # ============================================================================

# class AudioChunk:
#     """Represents a single audio chunk with metadata for seamless playback"""
#     def __init__(self, data: str, sequence: int, duration_ms: int, is_final: bool = False):
#         self.data = data
#         self.sequence = sequence
#         self.duration_ms = duration_ms
#         self.is_final = is_final
#         self.timestamp = time.time()

# class SeamlessMurfStreaming:
#     def __init__(self, api_key):
#         self.api_key = api_key
#         self.websocket = None
#         self.session_id = None
#         self.chunk_sequence = 0
#         self.sample_rate = 24000
#         self.channels = 1
#         self.format = "WAV"
        
#     async def connect(self, session_id: str = None):
#         try:
#             self.session_id = session_id or f"session_{int(time.time())}"
            
#             # Reuse existing connection if available
#             if session_id in websocket_pool and websocket_pool[session_id].get('websocket'):
#                 existing_ws = websocket_pool[session_id]['websocket']
#                 if not existing_ws.closed:
#                     self.websocket = existing_ws
#                     logger.info(f"Reusing WebSocket connection for session {session_id}")
#                     return True
            
#             # Create new connection
#             self.websocket = await websockets.connect(
#                 "wss://api.murf.ai/v1/speech/generate-speech",
#                 ping_interval=20,
#                 ping_timeout=10,
#                 close_timeout=10
#             )
            
#             # Send auth
#             auth_message = {
#                 "type": "auth",
#                 "apikey": self.api_key
#             }
#             await self.websocket.send(json.dumps(auth_message))
            
#             # Store in pool for reuse
#             websocket_pool[self.session_id] = {
#                 'websocket': self.websocket,
#                 'created_at': time.time()
#             }
            
#             logger.info(f"Connected to Murf WebSocket for session {self.session_id}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Murf connection failed: {e}")
#             return False
    
#     def calculate_chunk_duration(self, audio_data: str) -> int:
#         """Calculate approximate duration of audio chunk in milliseconds"""
#         try:
#             # Decode base64 to get byte size
#             audio_bytes = base64.b64decode(audio_data)
            
#             # For WAV: bytes_per_second = sample_rate * channels * bytes_per_sample
#             # Assuming 16-bit (2 bytes per sample)
#             bytes_per_second = self.sample_rate * self.channels * 2
#             duration_ms = (len(audio_bytes) / bytes_per_second) * 1000
            
#             return int(duration_ms)
#         except:
#             # Fallback: assume ~100ms chunks
#             return 100
    
#     async def stream_tts_seamless(self, text: str, voice_id: str = "en-US-natalie"):
#         """Stream text to Murf with enhanced timing for seamless playback"""
#         try:
#             context_id = f"ctx_{self.session_id}_{int(time.time() * 1000)}"
#             self.chunk_sequence = 0
            
#             # Send TTS request with optimized settings for streaming
#             tts_message = {
#                 "contextId": context_id,
#                 "voiceId": voice_id,
#                 "text": text,
#                 "rate": "0",
#                 "pitch": "0",
#                 "sampleRate": self.sample_rate,
#                 "format": self.format,
#                 "channelType": "MONO",
#                 "model": "GEN2",
#                 "streamingEnabled": True,
#                 "chunkSizeMs": 250
#             }
            
#             await self.websocket.send(json.dumps(tts_message))
#             logger.info(f"Sent seamless TTS request for: {text[:50]}...")
            
#             total_duration = 0
            
#             # Listen for audio chunks with enhanced timing
#             while True:
#                 try:
#                     message = await asyncio.wait_for(self.websocket.recv(), timeout=15.0)
#                     data = json.loads(message)
                    
#                     if data.get('contextId') == context_id:
#                         if data.get('audioContent') or data.get('audio'):
#                             audio_data = data.get('audioContent') or data.get('audio')
                            
#                             # Calculate chunk duration for timing
#                             chunk_duration = self.calculate_chunk_duration(audio_data)
#                             total_duration += chunk_duration
                            
#                             # Create enhanced audio chunk with metadata
#                             chunk = AudioChunk(
#                                 data=audio_data,
#                                 sequence=self.chunk_sequence,
#                                 duration_ms=chunk_duration,
#                                 is_final=data.get('is_final', False)
#                             )
                            
#                             self.chunk_sequence += 1
#                             yield chunk
                            
#                         if data.get('is_final'):
#                             logger.info(f"TTS streaming complete - Total duration: {total_duration}ms")
#                             # Send final marker chunk
#                             final_chunk = AudioChunk(
#                                 data="",
#                                 sequence=self.chunk_sequence,
#                                 duration_ms=0,
#                                 is_final=True
#                             )
#                             yield final_chunk
#                             break
                            
#                 except asyncio.TimeoutError:
#                     logger.warning("TTS timeout - finishing stream")
#                     break
                    
#         except Exception as e:
#             logger.error(f"Seamless TTS streaming error: {e}")
#             yield None

#     async def cleanup(self):
#         """Clean up WebSocket connection"""
#         try:
#             if self.websocket and not self.websocket.closed:
#                 await self.websocket.close()
#             if self.session_id in websocket_pool:
#                 del websocket_pool[self.session_id]
#         except Exception as e:
#             logger.error(f"WebSocket cleanup error: {e}")

# # ============================================================================
# # INITIALIZATION AND UTILITIES
# # ============================================================================

# # Initialize API functions
# def initialize_apis():
#     """Initialize all API clients with proper error handling"""
#     global client, gemini_model
    
#     api_status = {
#         "assemblyai": False,
#         "murf": False,
#         "gemini": False,
#         "errors": []
#     }

#     # Initialize AssemblyAI
#     try:
#         if ASSEMBLYAI_API_KEY:
#             aai.settings.api_key = ASSEMBLYAI_API_KEY
#             api_status["assemblyai"] = True
#             logger.info("AssemblyAI initialized successfully")
#         else:
#             api_status["errors"].append("AssemblyAI API key not configured")
#     except Exception as e:
#         api_status["errors"].append(f"AssemblyAI initialization failed: {str(e)}")
    
#     # Initialize Murf
#     try:
#         if MURF_API_KEY:
#             client = Murf(api_key=MURF_API_KEY)
#             api_status["murf"] = True
#             logger.info("Murf initialized successfully")
#         else:
#             api_status["errors"].append("Murf API key not configured")
#     except Exception as e:
#         api_status["errors"].append(f"Murf initialization failed: {str(e)}")
    
#     # Initialize Gemini
#     try:
#         if GEMINI_API_KEY:
#             genai.configure(api_key=GEMINI_API_KEY)
#             gemini_model = genai.GenerativeModel('gemini-1.5-flash')
#             api_status["gemini"] = True
#             logger.info("Gemini initialized successfully")
#         else:
#             api_status["errors"].append("Gemini API key not configured")
#     except Exception as e:
#         api_status["errors"].append(f"Gemini initialization failed: {str(e)}")
    
#     return api_status

# # In-memory chat history storage
# CHAT_HISTORY: Dict[str, List[Dict]] = {}

# # Initialize APIs on startup
# api_status = initialize_apis()

# # Utility functions
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
#         prompt = f"You are a helpful AI assistant. Please respond conversationally (maximum 2500 characters) to: {new_user_message}"
#     else:
#         context = "\n".join(conversation[:-1])
#         prompt = f"""You are a helpful AI assistant. Here's our conversation so far:

# {context}

# Now the user says: {new_user_message}

# Please respond naturally and conversationally (maximum 2500 characters):"""
    
#     return prompt

# # Processing functions
# async def process_speech_to_text(audio_bytes: bytes) -> str:
#     """Process speech to text using AssemblyAI"""
#     try:
#         if not ASSEMBLYAI_API_KEY:
#             raise ValueError("AssemblyAI API key not configured")
        
#         logger.info(f"Starting transcription for {len(audio_bytes)} bytes")
        
#         if len(audio_bytes) == 0:
#             raise ValueError("Empty audio data received")
        
#         # Create a temporary file for AssemblyAI
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
#             temp_file.write(audio_bytes)
#             temp_file_path = temp_file.name
        
#         try:
#             transcriber = aai.Transcriber()
#             transcript = transcriber.transcribe(temp_file_path)
            
#             if transcript.status == aai.TranscriptStatus.error:
#                 raise ValueError(f"Transcription failed: {transcript.error}")
            
#             if not transcript.text or transcript.text.strip() == "":
#                 raise ValueError("No speech detected in audio")
                
#             logger.info(f"Transcription successful: {len(transcript.text)} characters")
#             return transcript.text.strip()
            
#         finally:
#             # Clean up temp file
#             try:
#                 os.unlink(temp_file_path)
#             except:
#                 pass
        
#     except Exception as e:
#         logger.error(f"STT processing error: {str(e)}")
#         raise

# async def process_llm_query(text: str, session_id: str) -> str:
#     """Process LLM query using Gemini"""
#     try:
#         if not gemini_model:
#             raise ValueError("Gemini API key not configured")
        
#         formatted_prompt = format_chat_for_gemini(session_id, text)
#         logger.info(f"Querying Gemini for session {session_id}")
        
#         response = gemini_model.generate_content(formatted_prompt)
        
#         if not response.text:
#             raise ValueError("No response generated from Gemini")
        
#         llm_response = response.text.strip()
#         logger.info(f"Gemini response generated: {len(llm_response)} characters")
        
#         # Add messages to chat history
#         add_to_chat_history(session_id, "user", text)
#         add_to_chat_history(session_id, "assistant", llm_response)
        
#         return llm_response
        
#     except Exception as e:
#         logger.error(f"LLM processing error: {str(e)}")
#         raise

# # ============================================================================
# # MAIN CHAT ENDPOINTS - FIXED TO MATCH YOUR FRONTEND
# # ============================================================================

# # ============================================================================
# # MAIN CHAT ENDPOINTS - SEPARATE FOR AUDIO AND TEXT
# # ============================================================================

# # Key fixes for the backend:

# @app.post("/agent/chat/{session_id}")
# async def chat_with_audio(
#     session_id: str = Path(..., description="Session ID for chat history"),
#     audio: UploadFile = File(...),  # This matches the frontend FormData.append('audio', ...)
#     voiceId: Optional[str] = Form(default="en-US-natalie")
# ):
#     """Chat endpoint for audio input with streaming response"""
    
#     async def stream_response():
#         murf_streaming = None
#         try:
#             logger.info(f"Processing audio for session: {session_id}")
            
#             # Read audio content safely with error handling
#             try:
#                 if hasattr(audio, 'seek'):
#                     await audio.seek(0)
#                 audio_content = await audio.read()
#                 logger.info(f"Read audio file: {len(audio_content)} bytes, content-type: {audio.content_type}")
                
#                 if len(audio_content) == 0:
#                     yield f"data: {json.dumps({'type': 'error', 'message': 'Empty audio file received'})}\n\n"
#                     return
                    
#             except Exception as e:
#                 logger.error(f"Error reading audio file: {e}")
#                 yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to read audio: {str(e)}'})}\n\n"
#                 return
            
#             # 1. Speech-to-Text (simulate for now if API fails)
#             try:
#                 if ASSEMBLYAI_API_KEY:
#                     transcript = await process_speech_to_text(audio_content)
#                 else:
#                     # Fallback for testing
#                     transcript = "Hello, this is a test message from audio input"
                    
#                 yield f"data: {json.dumps({'type': 'transcript', 'text': transcript, 'role': 'user'})}\n\n"
#                 user_input = transcript
#             except Exception as e:
#                 logger.error(f"STT error: {e}")
#                 # Continue with fallback
#                 user_input = "I sent you an audio message"
#                 yield f"data: {json.dumps({'type': 'transcript', 'text': user_input, 'role': 'user'})}\n\n"
            
#             # 2. LLM Processing (simulate if needed)
#             try:
#                 if gemini_model:
#                     llm_response = await process_llm_query(user_input, session_id)
#                 else:
#                     # Fallback response for testing
#                     llm_response = "I received your message and I'm responding to help you test the audio streaming functionality."
#                     add_to_chat_history(session_id, "user", user_input)
#                     add_to_chat_history(session_id, "assistant", llm_response)
                    
#                 yield f"data: {json.dumps({'type': 'llm_response', 'text': llm_response, 'role': 'assistant'})}\n\n"
#             except Exception as e:
#                 logger.error(f"LLM error: {e}")
#                 llm_response = "I'm having trouble processing your request, but I'm here to help."
#                 yield f"data: {json.dumps({'type': 'llm_response', 'text': llm_response, 'role': 'assistant'})}\n\n"
            
#             # 3. TTS Streaming (simulate chunks for testing)
#             logger.info("Starting TTS streaming...")
            
#             if MURF_API_KEY:
#                 # Try real Murf streaming
#                 murf_streaming = SeamlessMurfStreaming(MURF_API_KEY)
                
#                 if await murf_streaming.connect(session_id):
#                     async for chunk in murf_streaming.stream_tts_seamless(llm_response, voiceId):
#                         if chunk and isinstance(chunk, AudioChunk):
#                             chunk_data = {
#                                 'type': 'audio_chunk',
#                                 'audio_data': chunk.data,
#                                 'sequence': chunk.sequence,
#                                 'duration_ms': chunk.duration_ms,
#                                 'is_final': chunk.is_final
#                             }
#                             yield f"data: {json.dumps(chunk_data)}\n\n"
                            
#                             if chunk.is_final:
#                                 break
#                 else:
#                     # Fallback to simulated chunks
#                     await simulate_audio_chunks(llm_response)
#             else:
#                 # Simulate audio chunks for testing
#                 async def simulate_audio_chunks(text):
#                     words = text.split()
#                     chunk_size = 5  # 5 words per chunk
                    
#                     for i in range(0, len(words), chunk_size):
#                         chunk_words = words[i:i + chunk_size]
#                         chunk_text = " ".join(chunk_words)
                        
#                         # Generate fake audio data (silence)
#                         fake_audio = base64.b64encode(b'\x00' * 1000).decode()  # 1000 bytes of silence
                        
#                         chunk_data = {
#                             'type': 'audio_chunk',
#                             'audio_data': fake_audio,
#                             'sequence': i // chunk_size,
#                             'duration_ms': len(chunk_words) * 200,  # ~200ms per word
#                             'is_final': False
#                         }
                        
#                         yield f"data: {json.dumps(chunk_data)}\n\n"
#                         await asyncio.sleep(0.2)  # 200ms delay between chunks
                    
#                     # Send final chunk
#                     final_chunk = {
#                         'type': 'audio_chunk',
#                         'audio_data': '',
#                         'sequence': 999,
#                         'duration_ms': 0,
#                         'is_final': True
#                     }
#                     yield f"data: {json.dumps(final_chunk)}\n\n"
                
#                 async for chunk_data in simulate_audio_chunks(llm_response):
#                     yield chunk_data
            
#             # Signal completion
#             yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
#         except Exception as e:
#             logger.error(f"Chat streaming error: {e}")
#             yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
#         finally:
#             if murf_streaming:
#                 try:
#                     await murf_streaming.cleanup()
#                 except:
#                     pass
    
#     return StreamingResponse(
#         stream_response(), 
#         media_type="text/event-stream",
#         headers={
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive",
#             "X-Accel-Buffering": "no"
#         }
#     )
# @app.post("/agent/chat/{session_id}/text")
# async def chat_with_text(
#     session_id: str = Path(..., description="Session ID for chat history"),
#     text: str = Form(...),
#     voiceId: Optional[str] = Form(default="en-US-natalie")
# ):
#     """Chat endpoint for text input with streaming response"""
    
#     async def stream_response():
#         murf_streaming = None
#         try:
#             # TEXT INPUT PROCESSING
#             logger.info(f"Processing text for session: {session_id}")
#             user_input = text.strip()
            
#             if not user_input:
#                 yield f"data: {json.dumps({'type': 'error', 'message': 'Empty text provided', 'session_id': session_id})}\n\n"
#                 return
                
#             yield f"data: {json.dumps({'type': 'transcript', 'text': text, 'role': 'user', 'session_id': session_id})}\n\n"
            
#             # LLM Processing
#             try:
#                 llm_response = await process_llm_query(user_input, session_id)
#                 yield f"data: {json.dumps({'type': 'llm_response', 'text': llm_response, 'role': 'assistant', 'session_id': session_id})}\n\n"
#             except Exception as e:
#                 yield f"data: {json.dumps({'type': 'error', 'message': f'LLM failed: {str(e)}', 'session_id': session_id})}\n\n"
#                 return
            
#             # Text-to-Speech Streaming
#             logger.info("Starting TTS streaming...")
            
#             if not MURF_API_KEY:
#                 yield f"data: {json.dumps({'type': 'error', 'message': 'Murf API key not found', 'session_id': session_id})}\n\n"
#                 return
            
#             # Initialize Murf streaming
#             murf_streaming = SeamlessMurfStreaming(MURF_API_KEY)
            
#             if await murf_streaming.connect(session_id):
#                 # Send audio configuration to client first
#                 audio_config = {
#                     'type': 'audio_config',
#                     'sample_rate': murf_streaming.sample_rate,
#                     'channels': murf_streaming.channels,
#                     'format': murf_streaming.format,
#                     'session_id': session_id
#                 }
#                 yield f"data: {json.dumps(audio_config)}\n\n"
                
#                 # Stream audio chunks
#                 buffer_time = 0
#                 async for chunk in murf_streaming.stream_tts_seamless(llm_response, voiceId):
#                     if chunk and isinstance(chunk, AudioChunk):
#                         chunk_data = {
#                             'type': 'audio_chunk',
#                             'audio_data': chunk.data,
#                             'sequence': chunk.sequence,
#                             'duration_ms': chunk.duration_ms,
#                             'is_final': chunk.is_final,
#                             'timestamp': chunk.timestamp,
#                             'buffer_time_ms': buffer_time,
#                             'session_id': session_id
#                         }
                        
#                         yield f"data: {json.dumps(chunk_data)}\n\n"
                        
#                         if chunk.is_final:
#                             logger.info("Audio streaming completed")
#                             break
                        
#                         # Calculate optimal delay for seamless playback
#                         optimal_delay = max(0, (chunk.duration_ms - 50) / 1000)  # 50ms processing buffer
#                         if optimal_delay > 0:
#                             await asyncio.sleep(optimal_delay)
                        
#                         buffer_time += chunk.duration_ms
                        
#             else:
#                 yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to connect to Murf WebSocket', 'session_id': session_id})}\n\n"
            
#             # Signal completion
#             yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id})}\n\n"
            
#         except Exception as e:
#             logger.error(f"Chat streaming error: {e}")
#             yield f"data: {json.dumps({'type': 'error', 'message': str(e), 'session_id': session_id})}\n\n"
#         finally:
#             # Clean up WebSocket connection
#             if murf_streaming:
#                 await murf_streaming.cleanup()
    
#     return StreamingResponse(
#         stream_response(), 
#         media_type="text/event-stream",
#         headers={
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive",
#             "X-Accel-Buffering": "no"
#         }
#     )

# # ============================================================================
# # SESSION HISTORY ENDPOINTS
# # ============================================================================

# @app.get("/agent/history/{session_id}")
# async def get_session_history(session_id: str):
#     """Get chat history for a session"""
#     try:
#         history = get_chat_history(session_id)
        
#         return {
#             "status": "success",
#             "session_id": session_id,
#             "history": history,
#             "conversation_turns": len([msg for msg in history if msg["role"] == "user"]),
#             "message_count": len(history)
#         }
        
#     except Exception as e:
#         logger.error(f"Error retrieving history for session {session_id}: {str(e)}")
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "status": "error",
#                 "error_message": str(e)
#             }
#         )

# @app.delete("/agent/history/{session_id}")
# async def clear_session_history(session_id: str):
#     """Clear chat history for a session"""
#     try:
#         if session_id in CHAT_HISTORY:
#             del CHAT_HISTORY[session_id]
        
#         return {
#             "status": "success",
#             "message": f"History cleared for session {session_id}"
#         }
        
#     except Exception as e:
#         logger.error(f"Error clearing history for session {session_id}: {str(e)}")
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "status": "error",
#                 "error_message": str(e)
#             }
#         )

# # ============================================================================
# # HEALTH AND STATUS ENDPOINTS
# # ============================================================================

# @app.get("/health")
# async def health_check():
#     """Comprehensive health check"""
#     try:
#         health_status = {
#             "status": "healthy" if all([
#                 api_status["assemblyai"], 
#                 api_status["murf"], 
#                 api_status["gemini"]
#             ]) else "degraded",
#             "timestamp": datetime.now().isoformat(),
#             "apis": {
#                 "assemblyai": {
#                     "configured": bool(ASSEMBLYAI_API_KEY),
#                     "status": "healthy" if api_status["assemblyai"] else "unavailable"
#                 },
#                 "murf": {
#                     "configured": bool(MURF_API_KEY),
#                     "sdk_available": client is not None,
#                     "websocket_connections": len(websocket_pool),
#                     "status": "healthy" if api_status["murf"] else "unavailable"
#                 },
#                 "gemini": {
#                     "configured": bool(GEMINI_API_KEY),
#                     "model": "gemini-1.5-flash" if gemini_model else None,
#                     "status": "healthy" if api_status["gemini"] else "unavailable"
#                 }
#             },
#             "chat_sessions": {
#                 "active_sessions": len(CHAT_HISTORY),
#                 "total_messages": sum(len(history) for history in CHAT_HISTORY.values())
#             },
#             "errors": api_status.get("errors", [])
#         }
        
#         return health_status
        
#     except Exception as e:
#         logger.error(f"Health check failed: {str(e)}")
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "status": "unhealthy",
#                 "error": str(e),
#                 "timestamp": datetime.now().isoformat()
#             }
#         )

# # Optional endpoints for browser requests
# @app.get("/favicon.ico")
# async def favicon():
#     """Return favicon or 404"""
#     favicon_path = static_dir / "favicon.ico"
#     if favicon_path.exists():
#         return FileResponse(favicon_path)
#     return JSONResponse({"message": "Favicon not found"}, status_code=404)

# @app.get("/sw.js")
# async def service_worker():
#     """Return service worker or 404"""
#     sw_path = static_dir / "sw.js" 
#     if sw_path.exists():
#         return FileResponse(sw_path)
#     return JSONResponse({"message": "Service worker not found"}, status_code=404)

# # WebSocket cleanup task
# async def cleanup_old_connections():
#     """Clean up old WebSocket connections"""
#     current_time = time.time()
#     expired_sessions = []
    
#     for session_id, conn_info in websocket_pool.items():
#         if current_time - conn_info['created_at'] > 3600:  # 1 hour timeout
#             expired_sessions.append(session_id)
    
#     for session_id in expired_sessions:
#         try:
#             if websocket_pool[session_id]['websocket']:
#                 await websocket_pool[session_id]['websocket'].close()
#             del websocket_pool[session_id]
#             logger.info(f"Cleaned up expired WebSocket for session {session_id}")
#         except Exception as e:
#             logger.error(f"Error cleaning up session {session_id}: {e}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)








from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from murf import Murf
from dotenv import load_dotenv
from pathlib import Path as PathLib
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
import assemblyai as aai
import os
import uuid
import tempfile
import requests
import json
from fastapi import Body
import httpx
import google.generativeai as genai
import logging
import traceback
from functools import wraps
import asyncio
import websockets
import base64
import wave
import struct
from collections import deque

# Initialize global variables at module level
client = None
gemini_model = None
websocket_pool = {}

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="AI Voice Agent")

# Mount static files (HTML, JS, etc.)
static_dir = PathLib("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Enhanced CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Configuration - Get from environment variables
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY") 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ============================================================================
# ENHANCED MURF WEBSOCKET STREAMING CLASS
# ============================================================================

class AudioChunk:
    """Represents a single audio chunk with metadata for seamless playback"""
    def __init__(self, data: str, sequence: int, duration_ms: int, is_final: bool = False):
        self.data = data
        self.sequence = sequence
        self.duration_ms = duration_ms
        self.is_final = is_final
        self.timestamp = time.time()

class SeamlessMurfStreaming:
    def __init__(self, api_key):
        self.api_key = api_key
        self.websocket = None
        self.session_id = None
        self.chunk_sequence = 0
        self.sample_rate = 24000
        self.channels = 1
        self.format = "WAV"
        
    async def connect(self, session_id: str = None):
        try:
            self.session_id = session_id or f"session_{int(time.time())}"
            
            # Reuse existing connection if available
            if session_id in websocket_pool and websocket_pool[session_id].get('websocket'):
                existing_ws = websocket_pool[session_id]['websocket']
                if not existing_ws.closed:
                    self.websocket = existing_ws
                    logger.info(f"Reusing WebSocket connection for session {session_id}")
                    return True
            
            # Create new connection
            self.websocket = await websockets.connect(
                "wss://api.murf.ai/v1/speech/generate-speech",
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            
            # Send auth
            auth_message = {
                "type": "auth",
                "apikey": self.api_key
            }
            await self.websocket.send(json.dumps(auth_message))
            
            # Store in pool for reuse
            websocket_pool[self.session_id] = {
                'websocket': self.websocket,
                'created_at': time.time()
            }
            
            logger.info(f"Connected to Murf WebSocket for session {self.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Murf connection failed: {e}")
            return False
    
    def calculate_chunk_duration(self, audio_data: str) -> int:
        """Calculate approximate duration of audio chunk in milliseconds"""
        try:
            # Decode base64 to get byte size
            audio_bytes = base64.b64decode(audio_data)
            
            # For WAV: bytes_per_second = sample_rate * channels * bytes_per_sample
            # Assuming 16-bit (2 bytes per sample)
            bytes_per_second = self.sample_rate * self.channels * 2
            duration_ms = (len(audio_bytes) / bytes_per_second) * 1000
            
            return int(duration_ms)
        except:
            # Fallback: assume ~100ms chunks
            return 100
    
    async def stream_tts_seamless(self, text: str, voice_id: str = "en-US-natalie"):
        """Stream text to Murf with enhanced timing for seamless playback"""
        try:
            context_id = f"ctx_{self.session_id}_{int(time.time() * 1000)}"
            self.chunk_sequence = 0
            
            # Send TTS request with optimized settings for streaming
            tts_message = {
                "contextId": context_id,
                "voiceId": voice_id,
                "text": text,
                "rate": "0",
                "pitch": "0",
                "sampleRate": self.sample_rate,
                "format": self.format,
                "channelType": "MONO",
                "model": "GEN2",
                "streamingEnabled": True,
                "chunkSizeMs": 250
            }
            
            await self.websocket.send(json.dumps(tts_message))
            logger.info(f"Sent seamless TTS request for: {text[:50]}...")
            
            total_duration = 0
            
            # Listen for audio chunks with enhanced timing
            while True:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=15.0)
                    data = json.loads(message)
                    
                    if data.get('contextId') == context_id:
                        if data.get('audioContent') or data.get('audio'):
                            audio_data = data.get('audioContent') or data.get('audio')
                            
                            # Calculate chunk duration for timing
                            chunk_duration = self.calculate_chunk_duration(audio_data)
                            total_duration += chunk_duration
                            
                            # Create enhanced audio chunk with metadata
                            chunk = AudioChunk(
                                data=audio_data,
                                sequence=self.chunk_sequence,
                                duration_ms=chunk_duration,
                                is_final=data.get('is_final', False)
                            )
                            
                            self.chunk_sequence += 1
                            yield chunk
                            
                        if data.get('is_final'):
                            logger.info(f"TTS streaming complete - Total duration: {total_duration}ms")
                            # Send final marker chunk
                            final_chunk = AudioChunk(
                                data="",
                                sequence=self.chunk_sequence,
                                duration_ms=0,
                                is_final=True
                            )
                            yield final_chunk
                            break
                            
                except asyncio.TimeoutError:
                    logger.warning("TTS timeout - finishing stream")
                    break
                    
        except Exception as e:
            logger.error(f"Seamless TTS streaming error: {e}")
            yield None

    async def cleanup(self):
        """Clean up WebSocket connection"""
        try:
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
            if self.session_id in websocket_pool:
                del websocket_pool[self.session_id]
        except Exception as e:
            logger.error(f"WebSocket cleanup error: {e}")

# ============================================================================
# INITIALIZATION AND UTILITIES
# ============================================================================

# Initialize API functions
def initialize_apis():
    """Initialize all API clients with proper error handling"""
    global client, gemini_model
    
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
    except Exception as e:
        api_status["errors"].append(f"AssemblyAI initialization failed: {str(e)}")
    
    # Initialize Murf
    try:
        if MURF_API_KEY:
            client = Murf(api_key=MURF_API_KEY)
            api_status["murf"] = True
            logger.info("Murf initialized successfully")
        else:
            api_status["errors"].append("Murf API key not configured")
    except Exception as e:
        api_status["errors"].append(f"Murf initialization failed: {str(e)}")
    
    # Initialize Gemini
    try:
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            api_status["gemini"] = True
            logger.info("Gemini initialized successfully")
        else:
            api_status["errors"].append("Gemini API key not configured")
    except Exception as e:
        api_status["errors"].append(f"Gemini initialization failed: {str(e)}")
    
    return api_status

# In-memory chat history storage
CHAT_HISTORY: Dict[str, List[Dict]] = {}

# Initialize APIs on startup
api_status = initialize_apis()

# Utility functions
def get_chat_history(session_id: str) -> List[Dict]:
    """Get chat history for a session"""
    return CHAT_HISTORY.get(session_id, [])

def add_to_chat_history(session_id: str, role: str, content: str):
    """Add a message to chat history"""
    if session_id not in CHAT_HISTORY:
        CHAT_HISTORY[session_id] = []
    
    CHAT_HISTORY[session_id].append({
        "role": role,
        "content": content,
        "timestamp": time.time()
    })

def format_chat_for_gemini(session_id: str, new_user_message: str) -> str:
    """Format chat history for Gemini API"""
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
        prompt = f"You are a helpful AI assistant. Please respond conversationally (maximum 2500 characters) to: {new_user_message}"
    else:
        context = "\n".join(conversation[:-1])
        prompt = f"""You are a helpful AI assistant. Here's our conversation so far:

{context}

Now the user says: {new_user_message}

Please respond naturally and conversationally (maximum 2500 characters):"""
    
    return prompt

# Processing functions
async def process_speech_to_text(audio_bytes: bytes) -> str:
    """Process speech to text using AssemblyAI"""
    try:
        if not ASSEMBLYAI_API_KEY:
            raise ValueError("AssemblyAI API key not configured")
        
        logger.info(f"Starting transcription for {len(audio_bytes)} bytes")
        
        if len(audio_bytes) == 0:
            raise ValueError("Empty audio data received")
        
        # Create a temporary file for AssemblyAI
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(temp_file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                raise ValueError(f"Transcription failed: {transcript.error}")
            
            if not transcript.text or transcript.text.strip() == "":
                raise ValueError("No speech detected in audio")
                
            logger.info(f"Transcription successful: {len(transcript.text)} characters")
            return transcript.text.strip()
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
    except Exception as e:
        logger.error(f"STT processing error: {str(e)}")
        raise

async def process_llm_query(text: str, session_id: str) -> str:
    """Process LLM query using Gemini"""
    try:
        if not gemini_model:
            raise ValueError("Gemini API key not configured")
        
        formatted_prompt = format_chat_for_gemini(session_id, text)
        logger.info(f"Querying Gemini for session {session_id}")
        
        response = gemini_model.generate_content(formatted_prompt)
        
        if not response.text:
            raise ValueError("No response generated from Gemini")
        
        llm_response = response.text.strip()
        logger.info(f"Gemini response generated: {len(llm_response)} characters")
        
        # Add messages to chat history
        add_to_chat_history(session_id, "user", text)
        add_to_chat_history(session_id, "assistant", llm_response)
        
        return llm_response
        
    except Exception as e:
        logger.error(f"LLM processing error: {str(e)}")
        raise

# ============================================================================
# FIXED AUDIO CHUNK GENERATION FOR TESTING
# ============================================================================

async def generate_test_audio_chunks(text: str, voice_id: str = "en-US-natalie"):
    """Generate realistic test audio chunks for development/testing"""
    words = text.split()
    chunk_size = 5  # words per chunk
    sample_rate = 24000
    chunk_duration_ms = 300  # 300ms per chunk
    
    # Generate WAV header for 24kHz mono 16-bit
    def create_wav_chunk(duration_ms: int, frequency: int = 440) -> str:
        """Create a simple WAV audio chunk with a tone"""
        sample_rate = 24000
        samples = int(sample_rate * duration_ms / 1000)
        
        # WAV header (44 bytes)
        wav_data = bytearray()
        wav_data.extend(b'RIFF')
        wav_data.extend((samples * 2 + 36).to_bytes(4, 'little'))  # file size
        wav_data.extend(b'WAVE')
        wav_data.extend(b'fmt ')
        wav_data.extend((16).to_bytes(4, 'little'))  # PCM format chunk size
        wav_data.extend((1).to_bytes(2, 'little'))   # PCM format
        wav_data.extend((1).to_bytes(2, 'little'))   # mono
        wav_data.extend(sample_rate.to_bytes(4, 'little'))  # sample rate
        wav_data.extend((sample_rate * 2).to_bytes(4, 'little'))  # byte rate
        wav_data.extend((2).to_bytes(2, 'little'))   # block align
        wav_data.extend((16).to_bytes(2, 'little'))  # bits per sample
        wav_data.extend(b'data')
        wav_data.extend((samples * 2).to_bytes(4, 'little'))  # data size
        
        # Generate audio samples (simple silence for testing)
        for i in range(samples):
            # Generate very quiet tone so it's actually playable
            sample_value = int(1000 * 0.1)  # Very quiet
            wav_data.extend(sample_value.to_bytes(2, 'little', signed=True))
        
        return base64.b64encode(wav_data).decode('utf-8')
    
    sequence = 0
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        
        # Generate actual WAV data
        audio_data = create_wav_chunk(chunk_duration_ms, 440 + (sequence * 50))
        
        chunk = AudioChunk(
            data=audio_data,
            sequence=sequence,
            duration_ms=chunk_duration_ms,
            is_final=False
        )
        
        logger.info(f"Generated test chunk {sequence}: {len(audio_data)} bytes, {chunk_duration_ms}ms")
        yield chunk
        
        sequence += 1
        await asyncio.sleep(0.1)  # Small delay between chunks
    
    # Send final chunk
    final_chunk = AudioChunk(
        data="",
        sequence=sequence,
        duration_ms=0,
        is_final=True
    )
    yield final_chunk

# ============================================================================
# MAIN CHAT ENDPOINTS - ENHANCED WITH FIXED AUDIO STREAMING
# ============================================================================

@app.post("/agent/chat/{session_id}")
async def chat_with_audio(
    session_id: str = Path(..., description="Session ID for chat history"),
    audio: UploadFile = File(...),
    voiceId: Optional[str] = Form(default="en-US-natalie")
):
    """Chat endpoint for audio input with streaming response"""
    
    async def stream_response():
        murf_streaming = None
        try:
            logger.info(f"Processing audio for session: {session_id}")
            
            # Read audio content safely with error handling
            try:
                if hasattr(audio, 'seek'):
                    await audio.seek(0)
                audio_content = await audio.read()
                logger.info(f"Read audio file: {len(audio_content)} bytes, content-type: {audio.content_type}")
                
                if len(audio_content) == 0:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Empty audio file received'})}\n\n"
                    return
                    
            except Exception as e:
                logger.error(f"Error reading audio file: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to read audio: {str(e)}'})}\n\n"
                return
            
            # 1. Speech-to-Text
            try:
                if ASSEMBLYAI_API_KEY:
                    transcript = await process_speech_to_text(audio_content)
                else:
                    transcript = "Hello, this is a test message from audio input"
                    
                yield f"data: {json.dumps({'type': 'transcript', 'text': transcript, 'role': 'user'})}\n\n"
                user_input = transcript
            except Exception as e:
                logger.error(f"STT error: {e}")
                user_input = "I sent you an audio message"
                yield f"data: {json.dumps({'type': 'transcript', 'text': user_input, 'role': 'user'})}\n\n"
            
            # 2. LLM Processing
            try:
                if gemini_model:
                    llm_response = await process_llm_query(user_input, session_id)
                else:
                    llm_response = "I received your message and I'm responding to help you test the audio streaming functionality."
                    add_to_chat_history(session_id, "user", user_input)
                    add_to_chat_history(session_id, "assistant", llm_response)
                    
                yield f"data: {json.dumps({'type': 'llm_response', 'text': llm_response, 'role': 'assistant'})}\n\n"
            except Exception as e:
                logger.error(f"LLM error: {e}")
                llm_response = "I'm having trouble processing your request, but I'm here to help."
                yield f"data: {json.dumps({'type': 'llm_response', 'text': llm_response, 'role': 'assistant'})}\n\n"
            
            # 3. TTS Streaming - FIXED
            logger.info("Starting TTS streaming...")
            
            # Send audio configuration first
            audio_config = {
                'type': 'audio_config',
                'sample_rate': 24000,
                'channels': 1,
                'format': 'WAV'
            }
            yield f"data: {json.dumps(audio_config)}\n\n"
            
            if MURF_API_KEY:
                try:
                    murf_streaming = SeamlessMurfStreaming(MURF_API_KEY)
                    
                    if await murf_streaming.connect(session_id):
                        async for chunk in murf_streaming.stream_tts_seamless(llm_response, voiceId):
                            if chunk and isinstance(chunk, AudioChunk):
                                chunk_data = {
                                    'type': 'audio_chunk',
                                    'audio_data': chunk.data,
                                    'sequence': chunk.sequence,
                                    'duration_ms': chunk.duration_ms,
                                    'is_final': chunk.is_final
                                }
                                yield f"data: {json.dumps(chunk_data)}\n\n"
                                
                                if chunk.is_final:
                                    break
                    else:
                        raise Exception("Failed to connect to Murf WebSocket")
                        
                except Exception as e:
                    logger.error(f"Murf streaming failed: {e}, using test chunks")
                    # Fallback to test chunks
                    async for chunk in generate_test_audio_chunks(llm_response, voiceId):
                        if chunk:
                            chunk_data = {
                                'type': 'audio_chunk',
                                'audio_data': chunk.data,
                                'sequence': chunk.sequence,
                                'duration_ms': chunk.duration_ms,
                                'is_final': chunk.is_final
                            }
                            yield f"data: {json.dumps(chunk_data)}\n\n"
                            
                            if chunk.is_final:
                                break
            else:
                # Use test chunks when no API key
                async for chunk in generate_test_audio_chunks(llm_response, voiceId):
                    if chunk:
                        chunk_data = {
                            'type': 'audio_chunk',
                            'audio_data': chunk.data,
                            'sequence': chunk.sequence,
                            'duration_ms': chunk.duration_ms,
                            'is_final': chunk.is_final
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                        
                        if chunk.is_final:
                            break
            
            # Signal completion
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            if murf_streaming:
                try:
                    await murf_streaming.cleanup()
                except:
                    pass
    
    return StreamingResponse(
        stream_response(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/agent/chat/{session_id}/text")
async def chat_with_text(
    session_id: str = Path(..., description="Session ID for chat history"),
    text: str = Form(...),
    voiceId: Optional[str] = Form(default="en-US-natalie")
):
    """Chat endpoint for text input with streaming response"""
    
    async def stream_response():
        murf_streaming = None
        try:
            logger.info(f"Processing text for session: {session_id}")
            user_input = text.strip()
            
            if not user_input:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Empty text provided'})}\n\n"
                return
                
            yield f"data: {json.dumps({'type': 'transcript', 'text': text, 'role': 'user'})}\n\n"
            
            # LLM Processing
            try:
                if gemini_model:
                    llm_response = await process_llm_query(user_input, session_id)
                else:
                    llm_response = f"I received your message: '{user_input}'. This is a test response to help you verify the audio streaming functionality is working correctly."
                    add_to_chat_history(session_id, "user", user_input)
                    add_to_chat_history(session_id, "assistant", llm_response)
                    
                yield f"data: {json.dumps({'type': 'llm_response', 'text': llm_response, 'role': 'assistant'})}\n\n"
            except Exception as e:
                logger.error(f"LLM error: {e}")
                llm_response = "I'm having trouble processing your request, but I'm here to help."
                yield f"data: {json.dumps({'type': 'llm_response', 'text': llm_response, 'role': 'assistant'})}\n\n"
            
            # Send audio configuration
            audio_config = {
                'type': 'audio_config',
                'sample_rate': 24000,
                'channels': 1,
                'format': 'WAV'
            }
            yield f"data: {json.dumps(audio_config)}\n\n"
            
            # Text-to-Speech Streaming - FIXED
            logger.info("Starting TTS streaming...")
            
            if MURF_API_KEY:
                try:
                    murf_streaming = SeamlessMurfStreaming(MURF_API_KEY)
                    
                    if await murf_streaming.connect(session_id):
                        async for chunk in murf_streaming.stream_tts_seamless(llm_response, voiceId):
                            if chunk and isinstance(chunk, AudioChunk):
                                chunk_data = {
                                    'type': 'audio_chunk',
                                    'audio_data': chunk.data,
                                    'sequence': chunk.sequence,
                                    'duration_ms': chunk.duration_ms,
                                    'is_final': chunk.is_final,
                                    'timestamp': chunk.timestamp
                                }
                                
                                yield f"data: {json.dumps(chunk_data)}\n\n"
                                
                                if chunk.is_final:
                                    logger.info("Audio streaming completed")
                                    break
                    else:
                        raise Exception("Failed to connect to Murf WebSocket")
                        
                except Exception as e:
                    logger.error(f"Murf streaming failed: {e}, using test chunks")
                    # Fallback to test chunks
                    async for chunk in generate_test_audio_chunks(llm_response, voiceId):
                        if chunk:
                            chunk_data = {
                                'type': 'audio_chunk',
                                'audio_data': chunk.data,
                                'sequence': chunk.sequence,
                                'duration_ms': chunk.duration_ms,
                                'is_final': chunk.is_final,
                                'timestamp': chunk.timestamp
                            }
                            yield f"data: {json.dumps(chunk_data)}\n\n"
                            
                            if chunk.is_final:
                                break
            else:
                # Use test chunks when no API key
                async for chunk in generate_test_audio_chunks(llm_response, voiceId):
                    if chunk:
                        chunk_data = {
                            'type': 'audio_chunk',
                            'audio_data': chunk.data,
                            'sequence': chunk.sequence,
                            'duration_ms': chunk.duration_ms,
                            'is_final': chunk.is_final,
                            'timestamp': chunk.timestamp
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                        
                        if chunk.is_final:
                            break
            
            # Signal completion
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            if murf_streaming:
                await murf_streaming.cleanup()
    
    return StreamingResponse(
        stream_response(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================================
# SESSION HISTORY ENDPOINTS
# ============================================================================

@app.get("/agent/history/{session_id}")
async def get_session_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = get_chat_history(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "history": history,
            "conversation_turns": len([msg for msg in history if msg["role"] == "user"]),
            "message_count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving history for session {session_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_message": str(e)
            }
        )

@app.delete("/agent/history/{session_id}")
async def clear_session_history(session_id: str):
    """Clear chat history for a session"""
    try:
        if session_id in CHAT_HISTORY:
            del CHAT_HISTORY[session_id]
        
        return {
            "status": "success",
            "message": f"History cleared for session {session_id}"
        }
        
    except Exception as e:
        logger.error(f"Error clearing history for session {session_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_message": str(e)
            }
        )

# ============================================================================
# HEALTH AND STATUS ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
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
                    "websocket_connections": len(websocket_pool),
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

# Optional endpoints for browser requests
@app.get("/favicon.ico")
async def favicon():
    """Return favicon or 404"""
    favicon_path = static_dir / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return JSONResponse({"message": "Favicon not found"}, status_code=404)

@app.get("/sw.js")
async def service_worker():
    """Return service worker or 404"""
    sw_path = static_dir / "sw.js" 
    if sw_path.exists():
        return FileResponse(sw_path)
    return JSONResponse({"message": "Service worker not found"}, status_code=404)

# WebSocket cleanup task
async def cleanup_old_connections():
    """Clean up old WebSocket connections"""
    current_time = time.time()
    expired_sessions = []
    
    for session_id, conn_info in websocket_pool.items():
        if current_time - conn_info['created_at'] > 3600:  # 1 hour timeout
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        try:
            if websocket_pool[session_id]['websocket']:
                await websocket_pool[session_id]['websocket'].close()
            del websocket_pool[session_id]
            logger.info(f"Cleaned up expired WebSocket for session {session_id}")
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)