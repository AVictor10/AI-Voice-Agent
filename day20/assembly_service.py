# import os
# import queue
# import threading
# import assemblyai as aai
# from assemblyai.streaming.v3 import (
#     StreamingClient,
#     StreamingClientOptions,
#     StreamingParameters,
#     StreamingEvents,
#     BeginEvent,
#     TurnEvent,
#     TerminationEvent,
#     StreamingError
# )
# from dotenv import load_dotenv

# load_dotenv()

# class AssemblyAIStreamingClient:
#     def __init__(self, sample_rate: int = 16000):
#         # Get API key from environment
#         api_key = os.getenv("WEBSOCKET_ASSEMBLY_KEY")
#         if not api_key:
#             raise ValueError("❌ Missing WEBSOCKET_ASSEMBLY_KEY in .env file")

#         # Set API key globally
#         aai.settings.api_key = api_key
#         print(f"🔑 AssemblyAI API Key loaded: ...{api_key[-8:]}")

#         self.sample_rate = sample_rate
#         self.client = None
#         self.websocket = None  # Store WebSocket reference for sending messages
#         self.message_queue = queue.Queue()  # Thread-safe queue for messages
#         self._setup_client()

#     def set_websocket(self, websocket):
#         """Set the WebSocket connection for sending turn detection messages"""
#         self.websocket = websocket

#     def _setup_client(self):
#         """Setup the Universal-Streaming client with turn detection"""
        
#         def on_begin(client, event: BeginEvent):
#             print(f"✅ Universal-Streaming session started: {event.id}")

#         def on_turn(client, event: TurnEvent):
#             """Handle transcription turns WITH turn detection - Thread-safe version"""
#             if event.transcript:
#                 if event.end_of_turn:
#                     # 🔥 TURN DETECTION! User stopped talking
#                     print(f"🟢 END OF TURN: {event.transcript}")
                    
#                     # Put message in thread-safe queue
#                     data = {
#                         "type": "end_of_turn",
#                         "transcript": event.transcript,
#                         "turn_id": getattr(event, 'turn_order', 'unknown'),
#                         "confidence": getattr(event, 'end_of_turn_confidence', 0.0),
#                         "message": "🎯 User finished speaking!"
#                     }
#                     self.message_queue.put(data)
#                     print(f"📝 Queued end_of_turn message")
#                 else:
#                     # Partial transcript - user still talking
#                     print(f"🟡 PARTIAL: {event.transcript}")
                    
#                     # Put message in thread-safe queue
#                     data = {
#                         "type": "partial_transcript",
#                         "transcript": event.transcript,
#                         "message": "🗣️ User is speaking..."
#                     }
#                     self.message_queue.put(data)

#         def on_terminated(client, event: TerminationEvent):
#             print(f"🔒 Universal-Streaming session terminated. Audio duration: {event.audio_duration_seconds}s")

#         def on_error(client, error: StreamingError):
#             print(f"❌ Universal-Streaming error: {error}")

#         try:
#             # Create the StreamingClient for Universal-Streaming
#             self.client = StreamingClient(
#                 StreamingClientOptions(
#                     api_key=os.getenv("WEBSOCKET_ASSEMBLY_KEY")
#                 )
#             )
            
#             # Set up event handlers
#             self.client.on(StreamingEvents.Begin, on_begin)
#             self.client.on(StreamingEvents.Turn, on_turn)
#             self.client.on(StreamingEvents.Termination, on_terminated)
#             self.client.on(StreamingEvents.Error, on_error)
            
#             # Connect to AssemblyAI Universal-Streaming with turn detection optimized
#             self.client.connect(
#                 StreamingParameters(
#                     sample_rate=self.sample_rate,
#                     formatted_finals=True,  # Get formatted text for better display
#                     # Turn detection parameters for better responsiveness
#                     min_end_of_turn_silence_when_confident=200,  # 200ms silence
#                     max_end_of_turn_silence=1000,  # 1 second max silence
#                     end_of_turn_confidence_threshold=0.7,  # 70% confidence
#                 )
#             )
#             print("🔗 Connected to AssemblyAI Universal-Streaming with Turn Detection")
            
#         except Exception as e:
#             print(f"❌ Failed to setup Universal-Streaming client: {e}")
#             raise e

#     async def process_pending_messages(self):
#         """Process any pending messages from the queue - call this from your WebSocket loop"""
#         messages_sent = 0
#         while not self.message_queue.empty() and self.websocket:
#             try:
#                 data = self.message_queue.get_nowait()
#                 await self.websocket.send_json(data)
#                 print(f"📤 Sent {data['type']} to client: {data['transcript'][:50]}...")
#                 messages_sent += 1
#             except queue.Empty:
#                 break
#             except Exception as e:
#                 print(f"❌ Error sending message: {e}")
#                 break
#         return messages_sent

#     def stream(self, audio_chunk: bytes):
#         """Stream audio data to AssemblyAI Universal-Streaming"""
#         if self.client:
#             try:
#                 self.client.stream(audio_chunk)
#             except Exception as e:
#                 print(f"❌ Error streaming audio: {e}")

#     def close(self):
#         """Close the connection to AssemblyAI"""
#         if self.client:
#             try:
#                 self.client.disconnect()
#                 print("🔌 AssemblyAI Universal-Streaming connection closed")
#             except Exception as e:
#                 print(f"❌ Error closing client: {e}")
#             finally:
#                 self.client = None
#                 self.websocket = None






# import os
# import queue
# import threading
# import asyncio
# import json
# from typing import AsyncGenerator
# import aiohttp
# import assemblyai as aai
# from assemblyai.streaming.v3 import (
#     StreamingClient,
#     StreamingClientOptions,
#     StreamingParameters,
#     StreamingEvents,
#     BeginEvent,
#     TurnEvent,
#     TerminationEvent,
#     StreamingError
# )
# from dotenv import load_dotenv

# load_dotenv()

# class AssemblyAIStreamingClient:
#     def __init__(self, sample_rate: int = 16000):
#         # Get API key from environment
#         api_key = os.getenv("WEBSOCKET_ASSEMBLY_KEY")
#         if not api_key:
#             raise ValueError("❌ Missing WEBSOCKET_ASSEMBLY_KEY in .env file")

#         # Set API key globally
#         aai.settings.api_key = api_key
#         print(f"🔑 AssemblyAI API Key loaded: ...{api_key[-8:]}")

#         # Get OpenAI API key for LLM
#         self.openai_api_key = os.getenv("OPENAI_API_KEY")
#         if not self.openai_api_key:
#             print("⚠️ Warning: OPENAI_API_KEY not found in .env - LLM responses disabled")
#         else:
#             print("🔑 OpenAI API Key loaded for LLM streaming")

#         self.sample_rate = sample_rate
#         self.client = None
#         self.websocket = None  # Store WebSocket reference for sending messages
#         self.message_queue = queue.Queue()  # Thread-safe queue for messages
#         self._setup_client()

#     def set_websocket(self, websocket):
#         """Set the WebSocket connection for sending turn detection messages"""
#         self.websocket = websocket

#     def _setup_client(self):
#         """Setup the Universal-Streaming client with turn detection"""
        
#         def on_begin(client, event: BeginEvent):
#             print(f"✅ Universal-Streaming session started: {event.id}")

#         def on_turn(client, event: TurnEvent):
#             """Handle transcription turns WITH turn detection - Thread-safe version"""
#             if event.transcript:
#                 if event.end_of_turn:
#                     # 🔥 TURN DETECTION! User stopped talking
#                     print(f"🟢 END OF TURN: {event.transcript}")
                    
#                     # Put message in thread-safe queue
#                     data = {
#                         "type": "end_of_turn",
#                         "transcript": event.transcript,
#                         "turn_id": getattr(event, 'turn_order', 'unknown'),
#                         "confidence": getattr(event, 'end_of_turn_confidence', 0.0),
#                         "message": "🎯 User finished speaking!"
#                     }
#                     self.message_queue.put(data)
#                     print(f"📝 Queued end_of_turn message")
                    
#                     # 🤖 NEW: Queue LLM processing for final transcript
#                     if self.openai_api_key and event.transcript.strip():
#                         llm_task = {
#                             "type": "llm_process",
#                             "transcript": event.transcript.strip()
#                         }
#                         self.message_queue.put(llm_task)
#                         print(f"🤖 Queued LLM processing for: {event.transcript[:50]}...")
                        
#                 else:
#                     # Partial transcript - user still talking
#                     print(f"🟡 PARTIAL: {event.transcript}")
                    
#                     # Put message in thread-safe queue
#                     data = {
#                         "type": "partial_transcript",
#                         "transcript": event.transcript,
#                         "message": "🗣️ User is speaking..."
#                     }
#                     self.message_queue.put(data)

#         def on_terminated(client, event: TerminationEvent):
#             print(f"🔒 Universal-Streaming session terminated. Audio duration: {event.audio_duration_seconds}s")

#         def on_error(client, error: StreamingError):
#             print(f"❌ Universal-Streaming error: {error}")

#         try:
#             # Create the StreamingClient for Universal-Streaming
#             self.client = StreamingClient(
#                 StreamingClientOptions(
#                     api_key=os.getenv("WEBSOCKET_ASSEMBLY_KEY")
#                 )
#             )
            
#             # Set up event handlers
#             self.client.on(StreamingEvents.Begin, on_begin)
#             self.client.on(StreamingEvents.Turn, on_turn)
#             self.client.on(StreamingEvents.Termination, on_terminated)
#             self.client.on(StreamingEvents.Error, on_error)
            
#             # Connect to AssemblyAI Universal-Streaming with turn detection optimized
#             self.client.connect(
#                 StreamingParameters(
#                     sample_rate=self.sample_rate,
#                     formatted_finals=True,  # Get formatted text for better display
#                     # Turn detection parameters for better responsiveness
#                     min_end_of_turn_silence_when_confident=200,  # 200ms silence
#                     max_end_of_turn_silence=1000,  # 1 second max silence
#                     end_of_turn_confidence_threshold=0.7,  # 70% confidence
#                 )
#             )
#             print("🔗 Connected to AssemblyAI Universal-Streaming with Turn Detection")
            
#         except Exception as e:
#             print(f"❌ Failed to setup Universal-Streaming client: {e}")
#             raise e

#     async def _stream_llm_response(self, user_message: str) -> AsyncGenerator[str, None]:
#         """Stream response from Groq API (FREE and FAST)"""
#         # Try Groq API first (free tier available)
#         groq_api_key = os.getenv("GROQ_API_KEY")
        
#         if groq_api_key:
#             async for chunk in self._stream_groq_response(user_message, groq_api_key):
#                 yield chunk
#             return
        
#         # Fallback to OpenAI if Groq not available
#         if not self.openai_api_key:
#             yield "No API key configured. Get free Groq API key at https://console.groq.com"
#             return
            
#         headers = {
#             "Authorization": f"Bearer {self.openai_api_key}",
#             "Content-Type": "application/json"
#         }
        
#         payload = {
#             "model": "gpt-3.5-turbo",
#             "messages": [
#                 {
#                     "role": "system", 
#                     "content": "You are a helpful AI assistant. Provide concise, helpful responses."
#                 },
#                 {
#                     "role": "user", 
#                     "content": user_message
#                 }
#             ],
#             "stream": True,
#             "temperature": 0.7,
#             "max_tokens": 150
#         }
        
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.post(
#                     "https://api.openai.com/v1/chat/completions",
#                     headers=headers,
#                     json=payload
#                 ) as response:
                    
#                     if response.status != 200:
#                         error_text = await response.text()
#                         yield f"OpenAI API Error: {response.status} - {error_text}"
#                         return
                    
#                     async for line in response.content:
#                         if line:
#                             line = line.decode('utf-8').strip()
                            
#                             if line.startswith("data: "):
#                                 data = line[6:]  # Remove "data: " prefix
                                
#                                 if data == "[DONE]":
#                                     break
                                    
#                                 try:
#                                     json_data = json.loads(data)
                                    
#                                     if "choices" in json_data and len(json_data["choices"]) > 0:
#                                         delta = json_data["choices"][0].get("delta", {})
#                                         content = delta.get("content", "")
                                        
#                                         if content:
#                                             yield content
                                            
#                                 except json.JSONDecodeError:
#                                     continue
                                    
#         except Exception as e:
#             yield f"LLM Error: {str(e)}"

#     async def _stream_groq_response(self, user_message: str, api_key: str) -> AsyncGenerator[str, None]:
#         """Stream response from Groq API (FREE and very fast)"""
#         headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json"
#         }
        
#         payload = {
#             "model": "llama3-8b-8192",  # Fast free model
#             "messages": [
#                 {
#                     "role": "system", 
#                     "content": "You are a helpful AI assistant. Provide concise, helpful responses."
#                 },
#                 {
#                     "role": "user", 
#                     "content": user_message
#                 }
#             ],
#             "stream": True,
#             "temperature": 0.7,
#             "max_tokens": 150
#         }
        
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.post(
#                     "https://api.groq.com/openai/v1/chat/completions",
#                     headers=headers,
#                     json=payload
#                 ) as response:
                    
#                     if response.status != 200:
#                         error_text = await response.text()
#                         yield f"Groq API Error: {response.status} - {error_text}"
#                         return
                    
#                     async for line in response.content:
#                         if line:
#                             line = line.decode('utf-8').strip()
                            
#                             if line.startswith("data: "):
#                                 data = line[6:]  # Remove "data: " prefix
                                
#                                 if data == "[DONE]":
#                                     break
                                    
#                                 try:
#                                     json_data = json.loads(data)
                                    
#                                     if "choices" in json_data and len(json_data["choices"]) > 0:
#                                         delta = json_data["choices"][0].get("delta", {})
#                                         content = delta.get("content", "")
                                        
#                                         if content:
#                                             yield content
                                            
#                                 except json.JSONDecodeError:
#                                     continue
                                    
#         except Exception as e:
#             yield f"Groq Error: {str(e)}"

#     async def process_pending_messages(self):
#         """Process any pending messages from the queue - call this from your WebSocket loop"""
#         messages_sent = 0
#         while not self.message_queue.empty() and self.websocket:
#             try:
#                 data = self.message_queue.get_nowait()
                
#                 if data["type"] == "llm_process":
#                     # 🤖 Process LLM request
#                     await self._handle_llm_request(data["transcript"])
#                     messages_sent += 1
#                 else:
#                     # Regular WebSocket message
#                     await self.websocket.send_json(data)
#                     print(f"📤 Sent {data['type']} to client: {data['transcript'][:50]}...")
#                     messages_sent += 1
                    
#             except queue.Empty:
#                 break
#             except Exception as e:
#                 print(f"❌ Error sending message: {e}")
#                 break
#         return messages_sent

#     async def _handle_llm_request(self, user_transcript: str):
#         """Handle LLM streaming request and accumulate response"""
#         print(f"\n🤖 LLM Processing: '{user_transcript}'")
#         print("🤖 LLM Response: ", end="", flush=True)
        
#         accumulated_response = ""
        
#         try:
#             async for chunk in self._stream_llm_response(user_transcript):
#                 print(chunk, end="", flush=True)
#                 accumulated_response += chunk
                
#             print(f"\n🤖 Complete Response: {accumulated_response}")
#             print("="*60)
            
#         except Exception as e:
#             print(f"\n❌ LLM Error: {e}")

#     def stream(self, audio_chunk: bytes):
#         """Stream audio data to AssemblyAI Universal-Streaming"""
#         if self.client:
#             try:
#                 self.client.stream(audio_chunk)
#             except Exception as e:
#                 print(f"❌ Error streaming audio: {e}")

#     def close(self):
#         """Close the connection to AssemblyAI"""
#         if self.client:
#             try:
#                 self.client.disconnect()
#                 print("🔌 AssemblyAI Universal-Streaming connection closed")
#             except Exception as e:
#                 print(f"❌ Error closing client: {e}")
#             finally:
#                 self.client = None
#                 self.websocket = None






import os
import queue
import threading
import asyncio
import json
import websockets
from typing import AsyncGenerator
import aiohttp
import assemblyai as aai
from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingParameters,
    StreamingEvents,
    BeginEvent,
    TurnEvent,
    TerminationEvent,
    StreamingError
)
from dotenv import load_dotenv
import base64

load_dotenv()

class AssemblyAIStreamingClient:
    def __init__(self, sample_rate: int = 16000):
        # Get API key from environment
        api_key = os.getenv("WEBSOCKET_ASSEMBLY_KEY")
        if not api_key:
            raise ValueError("❌ Missing WEBSOCKET_ASSEMBLY_KEY in .env file")

        # Set API key globally
        aai.settings.api_key = api_key
        print(f"🔑 AssemblyAI API Key loaded: ...{api_key[-8:]}")

        # Get OpenAI API key for LLM
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️ Warning: OPENAI_API_KEY not found in .env - LLM responses disabled")
        else:
            print("🔑 OpenAI API Key loaded for LLM streaming")

        # Get Murf API credentials
        self.murf_api_key = os.getenv("MURF_API_KEY")
        if not self.murf_api_key:
            print("⚠️ Warning: MURF_API_KEY not found - TTS disabled")
        else:
            print("🔊 Murf TTS credentials loaded")

        self.sample_rate = sample_rate
        self.client = None
        self.websocket = None  # Store WebSocket reference for sending messages
        self.message_queue = queue.Queue()  # Thread-safe queue for messages
        self.murf_websocket = None  # Murf WebSocket connection
        self.context_id = "static_context_2024"  # Static context ID as requested
        self._setup_client()

    def set_websocket(self, websocket):
        """Set the WebSocket connection for sending turn detection messages"""
        self.websocket = websocket

    def _setup_client(self):
        """Setup the Universal-Streaming client with turn detection"""
        
        def on_begin(client, event: BeginEvent):
            print(f"✅ Universal-Streaming session started: {event.id}")

        def on_turn(client, event: TurnEvent):
            """Handle transcription turns WITH turn detection - Thread-safe version"""
            if event.transcript:
                if event.end_of_turn:
                    # 🔥 TURN DETECTION! User stopped talking
                    print(f"🟢 END OF TURN: {event.transcript}")
                    
                    # Put message in thread-safe queue
                    data = {
                        "type": "end_of_turn",
                        "transcript": event.transcript,
                        "turn_id": getattr(event, 'turn_order', 'unknown'),
                        "confidence": getattr(event, 'end_of_turn_confidence', 0.0),
                        "message": "🎯 User finished speaking!"
                    }
                    self.message_queue.put(data)
                    print(f"📝 Queued end_of_turn message")
                    
                    # 🤖 NEW: Queue LLM processing for final transcript
                    if self.openai_api_key and event.transcript.strip():
                        llm_task = {
                            "type": "llm_process",
                            "transcript": event.transcript.strip()
                        }
                        self.message_queue.put(llm_task)
                        print(f"🤖 Queued LLM processing for: {event.transcript[:50]}...")
                        
                else:
                    # Partial transcript - user still talking
                    print(f"🟡 PARTIAL: {event.transcript}")
                    
                    # Put message in thread-safe queue
                    data = {
                        "type": "partial_transcript",
                        "transcript": event.transcript,
                        "message": "🗣️ User is speaking..."
                    }
                    self.message_queue.put(data)

        def on_terminated(client, event: TerminationEvent):
            print(f"🔒 Universal-Streaming session terminated. Audio duration: {event.audio_duration_seconds}s")

        def on_error(client, error: StreamingError):
            print(f"❌ Universal-Streaming error: {error}")

        try:
            # Create the StreamingClient for Universal-Streaming
            self.client = StreamingClient(
                StreamingClientOptions(
                    api_key=os.getenv("WEBSOCKET_ASSEMBLY_KEY")
                )
            )
            
            # Set up event handlers
            self.client.on(StreamingEvents.Begin, on_begin)
            self.client.on(StreamingEvents.Turn, on_turn)
            self.client.on(StreamingEvents.Termination, on_terminated)
            self.client.on(StreamingEvents.Error, on_error)
            
            # Connect to AssemblyAI Universal-Streaming with turn detection optimized
            self.client.connect(
                StreamingParameters(
                    sample_rate=self.sample_rate,
                    formatted_finals=True,  # Get formatted text for better display
                    # Turn detection parameters for better responsiveness
                    min_end_of_turn_silence_when_confident=200,  # 200ms silence
                    max_end_of_turn_silence=1000,  # 1 second max silence
                    end_of_turn_confidence_threshold=0.7,  # 70% confidence
                )
            )
            print("🔗 Connected to AssemblyAI Universal-Streaming with Turn Detection")
            
        except Exception as e:
            print(f"❌ Failed to setup Universal-Streaming client: {e}")
            raise e

    async def _connect_to_murf_websocket(self):
        """Connect to Murf WebSocket API - Fixed URL and auth"""
        if not self.murf_api_key:
            print("❌ Murf API key not available")
            return None
            
        try:
            # Try different WebSocket URL patterns based on Murf docs
            websocket_urls = [
                f"wss://api.murf.ai/v1/speech/generate-speech?apikey={self.murf_api_key}",
                f"wss://api.murf.ai/v2/speech/generate?api-key={self.murf_api_key}",
                f"wss://api.murf.ai/ws/v1/speech?token={self.murf_api_key}"
            ]
            
            for url in websocket_urls:
                try:
                    print(f"🔊 Trying Murf WebSocket URL: {url.split('?')[0]}...")
                    
                    # Add headers that might be required
                    headers = {
                        "api-key": self.murf_api_key,
                        "Authorization": f"Bearer {self.murf_api_key}"
                    }
                    
                    self.murf_websocket = await websockets.connect(url, extra_headers=headers)
                    print("🔊 ✅ Connected to Murf TTS WebSocket successfully!")
                    return self.murf_websocket
                    
                except Exception as e:
                    print(f"❌ Failed with URL {url.split('?')[0]}: {e}")
                    continue
            
            print("❌ All WebSocket connection attempts failed")
            return None
            
        except Exception as e:
            print(f"❌ General WebSocket connection error: {e}")
            return None

    async def _get_valid_voice_id(self):
        """Get a valid voice ID from Murf API"""
        try:
            headers = {
                "api-key": self.murf_api_key,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.murf.ai/v1/speech/voices",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        voices_data = await response.json()
                        print(f"✅ Retrieved {len(voices_data) if isinstance(voices_data, list) else 'unknown'} voices from Murf")
                        
                        # Look for an English voice with specific preferences
                        preferred_voices = ["en-US-natalie", "en-US-jane", "en-US-john", "en-US-sarah"]
                        
                        if isinstance(voices_data, list):
                            # First try preferred voices
                            for preferred in preferred_voices:
                                for voice in voices_data:
                                    voice_id = voice.get("voiceId") or voice.get("id")
                                    if voice_id and preferred.lower() in voice_id.lower():
                                        print(f"🎤 Found preferred voice: {voice_id} - {voice.get('name', 'Unknown')}")
                                        return voice_id
                            
                            # Then try any English voice
                            for voice in voices_data:
                                if voice.get("language", "").lower().startswith("en"):
                                    voice_id = voice.get("voiceId") or voice.get("id")
                                    if voice_id:
                                        print(f"🎤 Found English voice: {voice_id} - {voice.get('name', 'Unknown')}")
                                        return voice_id
                            
                            # Finally, use first available
                            if len(voices_data) > 0:
                                first_voice = voices_data[0]
                                voice_id = first_voice.get("voiceId") or first_voice.get("id")
                                if voice_id:
                                    print(f"🎤 Using first available voice: {voice_id} - {first_voice.get('name', 'Unknown')}")
                                    return voice_id
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to get voices: {response.status} - {error_text}")
                        
        except Exception as e:
            print(f"❌ Error getting voice list: {e}")
        
        # Fallback to common voice IDs
        fallback_voices = ["en-US-natalie", "en-US-jane", "en-US-john"]
        selected_voice = fallback_voices[0]
        print(f"⚠️ Using fallback voice ID: {selected_voice}")
        return selected_voice

    async def _send_text_to_murf(self, text: str):
        """Send text to Murf TTS and get base64 audio - WebSocket first, HTTP fallback"""
        try:
            # Try WebSocket first
            if await self._try_murf_websocket(text):
                return await self._try_murf_websocket(text)
            
            # Fall back to HTTP API
            print("🔄 Using HTTP API for Murf TTS...")
            return await self._send_text_to_murf_http(text)
            
        except Exception as e:
            print(f"❌ Error in _send_text_to_murf: {e}")
            return await self._send_text_to_murf_http(text)

    async def _try_murf_websocket(self, text: str):
        """Try to use Murf WebSocket API"""
        try:
            # Get valid voice ID
            voice_id = await self._get_valid_voice_id()
            
            # Connect if not already connected
            if not self.murf_websocket:
                await self._connect_to_murf_websocket()
            
            if self.murf_websocket:
                # Prepare WebSocket request with different possible formats
                websocket_requests = [
                    {
                        "contextId": self.context_id,
                        "voiceId": voice_id,
                        "text": text,
                        "rate": "0",
                        "pitch": "0",
                        "sampleRate": 24000,
                        "format": "WAV",
                        "channelType": "MONO",
                        "model": "GEN2"
                    },
                    {
                        "context_id": self.context_id,
                        "voice_id": voice_id,
                        "text": text,
                        "speed": 1.0,
                        "pitch": 1.0,
                        "format": "wav",
                        "sample_rate": 24000
                    },
                    {
                        "action": "generate",
                        "contextId": self.context_id,
                        "voiceId": voice_id,
                        "text": text
                    }
                ]
                
                for request_format in websocket_requests:
                    try:
                        print(f"🔊 Sending WebSocket request format {websocket_requests.index(request_format) + 1}...")
                        await self.murf_websocket.send(json.dumps(request_format))
                        
                        # Wait for response with timeout
                        response = await asyncio.wait_for(self.murf_websocket.recv(), timeout=30)
                        response_data = json.loads(response)
                        
                        print(f"📥 WebSocket response keys: {list(response_data.keys())}")
                        
                        # Check for successful response
                        if (response_data.get("status") in ["SUCCESS", "success"] or 
                            "audioContent" in response_data or 
                            "audio_base64" in response_data):
                            
                            base64_audio = (response_data.get("audioContent") or 
                                          response_data.get("audio_base64") or
                                          response_data.get("audioData"))
                            
                            if base64_audio:
                                print("\n" + "="*80)
                                print("🎵 MURF TTS BASE64 AUDIO RECEIVED (WebSocket)!")
                                print("="*80)
                                print(f"Audio Length: {len(base64_audio)} characters")
                                print(f"Context ID: {response_data.get('contextId', 'N/A')}")
                                print(f"Voice ID: {voice_id}")
                                print("\nBase64 Audio Data:")
                                print("-" * 40)
                                self._print_base64_audio(base64_audio)
                                print("="*80)
                                return base64_audio
                        else:
                            print(f"❌ WebSocket request failed: {response_data}")
                            
                    except asyncio.TimeoutError:
                        print("❌ WebSocket request timed out")
                    except Exception as e:
                        print(f"❌ WebSocket request error: {e}")
                
                # Close failed WebSocket connection
                await self.murf_websocket.close()
                self.murf_websocket = None
                
        except Exception as e:
            print(f"❌ WebSocket attempt failed: {e}")
            
        return None

    async def _send_text_to_murf_http(self, text: str):
        """Send text to Murf via HTTP API and get base64 audio"""
        try:
            voice_id = await self._get_valid_voice_id()
            
            headers = {
                "api-key": self.murf_api_key,
                "Content-Type": "application/json"
            }
            
            # Try different payload formats
            payloads = [
                {
                    "text": text,
                    "voiceId": voice_id,
                    "audioFormat": "WAV",
                    "sampleRate": 24000,
                    "channelType": "MONO",
                    "model": "GEN2",
                    "returnBase64": True  # Request base64 format
                },
                {
                    "text": text,
                    "voiceId": voice_id,
                    "audioFormat": "WAV",
                    "sampleRate": 24000,
                    "channelType": "MONO",
                    "model": "GEN2"
                }
            ]
            
            print(f"🔊 Generating speech via HTTP API...")
            print(f"📝 Text: {text[:100]}...")
            print(f"🎤 Using voice: {voice_id}")
            
            async with aiohttp.ClientSession() as session:
                for i, payload in enumerate(payloads):
                    try:
                        print(f"🔄 Trying payload format {i+1}...")
                        
                        async with session.post(
                            "https://api.murf.ai/v1/speech/generate",
                            headers=headers,
                            json=payload
                        ) as response:
                            
                            if response.status == 200:
                                result = await response.json()
                                print(f"✅ HTTP API Success! Response keys: {list(result.keys())}")
                                
                                # Look for audio data in various fields
                                base64_audio = None
                                audio_url = None
                                
                                # Check for direct base64 audio
                                for field in ["encodedAudio", "audioContent", "audioData", "base64Audio", "audio"]:
                                    if field in result and result[field]:
                                        potential_audio = result[field]
                                        if isinstance(potential_audio, str) and len(potential_audio) > 1000:
                                            # This looks like base64 audio data
                                            if not potential_audio.startswith("http"):
                                                base64_audio = potential_audio
                                                print(f"📦 Found base64 audio in field: {field}")
                                                break
                                
                                # Check for audio URL to download
                                if not base64_audio:
                                    for field in ["audioFile", "audioUrl", "url"]:
                                        if field in result and result[field]:
                                            potential_url = result[field]
                                            if isinstance(potential_url, str) and potential_url.startswith("http"):
                                                audio_url = potential_url
                                                print(f"🔗 Found audio URL in field: {field}")
                                                break
                                
                                # If we have base64 audio, return it
                                if base64_audio:
                                    print("\n" + "="*80)
                                    print("🎵 MURF TTS BASE64 AUDIO RECEIVED (HTTP - Direct)!")
                                    print("="*80)
                                    print(f"Audio Length: {len(base64_audio)} characters")
                                    print(f"Voice ID: {voice_id}")
                                    print("\nBase64 Audio Data:")
                                    print("-" * 40)
                                    self._print_base64_audio(base64_audio)
                                    print("="*80)
                                    return base64_audio
                                
                                # If we have a URL, download and encode
                                elif audio_url:
                                    print(f"📥 Downloading audio from URL: {audio_url}")
                                    async with session.get(audio_url) as audio_response:
                                        if audio_response.status == 200:
                                            audio_data = await audio_response.read()
                                            base64_audio_encoded = base64.b64encode(audio_data).decode('utf-8')
                                            
                                            print("\n" + "="*80)
                                            print("🎵 MURF TTS BASE64 AUDIO RECEIVED (HTTP - Downloaded)!")
                                            print("="*80)
                                            print(f"Original URL: {audio_url}")
                                            print(f"Audio Length: {len(base64_audio_encoded)} characters")
                                            print(f"Voice ID: {voice_id}")
                                            print("\nBase64 Audio Data:")
                                            print("-" * 40)
                                            self._print_base64_audio(base64_audio_encoded)
                                            print("="*80)
                                            return base64_audio_encoded
                                        else:
                                            print(f"❌ Failed to download audio: {audio_response.status}")
                                
                                else:
                                    print(f"❌ No audio data found in response. Full response: {result}")
                                    
                            else:
                                error_text = await response.text()
                                print(f"❌ HTTP API Error {i+1}: {response.status}")
                                print(f"Error details: {error_text}")
                                
                    except Exception as e:
                        print(f"❌ Error with payload {i+1}: {e}")
                        continue
                        
        except Exception as e:
            print(f"❌ Error with Murf HTTP API: {e}")
            import traceback
            traceback.print_exc()
            
        return None

    def _print_base64_audio(self, base64_audio: str):
        """Helper method to print base64 audio in a readable format"""
        if len(base64_audio) > 400:
            print(base64_audio[:200])
            print(f"... [{len(base64_audio) - 400} characters omitted] ...")
            print(base64_audio[-200:])
        else:
            print(base64_audio)

    async def _stream_llm_response(self, user_message: str) -> AsyncGenerator[str, None]:
        """Stream response from Groq API (FREE and FAST)"""
        # Try Groq API first (free tier available)
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if groq_api_key:
            async for chunk in self._stream_groq_response(user_message, groq_api_key):
                yield chunk
            return
        
        # Fallback to OpenAI if Groq not available
        if not self.openai_api_key:
            yield "No API key configured. Get free Groq API key at https://console.groq.com"
            return
            
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Provide concise, helpful responses."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        yield f"OpenAI API Error: {response.status} - {error_text}"
                        return
                    
                    async for line in response.content:
                        if line:
                            line = line.decode('utf-8').strip()
                            
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                
                                if data == "[DONE]":
                                    break
                                    
                                try:
                                    json_data = json.loads(data)
                                    
                                    if "choices" in json_data and len(json_data["choices"]) > 0:
                                        delta = json_data["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        
                                        if content:
                                            yield content
                                            
                                except json.JSONDecodeError:
                                    continue
                                    
        except Exception as e:
            yield f"LLM Error: {str(e)}"

    async def _stream_groq_response(self, user_message: str, api_key: str) -> AsyncGenerator[str, None]:
        """Stream response from Groq API (FREE and very fast)"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",  # Fast free model
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Provide concise, helpful responses."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        yield f"Groq API Error: {response.status} - {error_text}"
                        return
                    
                    async for line in response.content:
                        if line:
                            line = line.decode('utf-8').strip()
                            
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                
                                if data == "[DONE]":
                                    break
                                    
                                try:
                                    json_data = json.loads(data)
                                    
                                    if "choices" in json_data and len(json_data["choices"]) > 0:
                                        delta = json_data["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        
                                        if content:
                                            yield content
                                            
                                except json.JSONDecodeError:
                                    continue
                                    
        except Exception as e:
            yield f"Groq Error: {str(e)}"

    async def process_pending_messages(self):
        """Process any pending messages from the queue - call this from your WebSocket loop"""
        messages_sent = 0
        while not self.message_queue.empty() and self.websocket:
            try:
                data = self.message_queue.get_nowait()
                
                if data["type"] == "llm_process":
                    # 🤖 Process LLM request
                    await self._handle_llm_request(data["transcript"])
                    messages_sent += 1
                else:
                    # Regular WebSocket message
                    await self.websocket.send_json(data)
                    print(f"📤 Sent {data['type']} to client: {data['transcript'][:50]}...")
                    messages_sent += 1
                    
            except queue.Empty:
                break
            except Exception as e:
                print(f"❌ Error sending message: {e}")
                break
        return messages_sent

    async def _handle_llm_request(self, user_transcript: str):
        """Handle LLM streaming request, accumulate response, and send to Murf TTS"""
        print(f"\n🤖 LLM Processing: '{user_transcript}'")
        print("🤖 LLM Response: ", end="", flush=True)
        
        accumulated_response = ""
        
        try:
            # Stream and accumulate LLM response
            async for chunk in self._stream_llm_response(user_transcript):
                print(chunk, end="", flush=True)
                accumulated_response += chunk
                
            print(f"\n🤖 Complete LLM Response: {accumulated_response}")
            
            # 🔊 Send complete response to Murf TTS
            if accumulated_response.strip():
                print(f"\n🔊 Sending LLM response to Murf TTS...")
                base64_audio = await self._send_text_to_murf(accumulated_response.strip())
                
                if base64_audio:
                    print("✅ Successfully received base64 audio from Murf!")
                    # The base64 audio is already printed in _send_text_to_murf methods
                else:
                    print("❌ Failed to get audio from Murf")
            
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ LLM/TTS Error: {e}")
            import traceback
            traceback.print_exc()

    def stream(self, audio_chunk: bytes):
        """Stream audio data to AssemblyAI Universal-Streaming"""
        if self.client:
            try:
                self.client.stream(audio_chunk)
            except Exception as e:
                print(f"❌ Error streaming audio: {e}")

    def close(self):
        """Close the connection to AssemblyAI and Murf"""
        if self.client:
            try:
                self.client.disconnect()
                print("🔌 AssemblyAI Universal-Streaming connection closed")
            except Exception as e:
                print(f"❌ Error closing AssemblyAI client: {e}")
            finally:
                self.client = None
                self.websocket = None
        
        # Close Murf WebSocket
        if self.murf_websocket:
            try:
                asyncio.create_task(self.murf_websocket.close())
                print("🔌 Murf TTS connection closed")
            except Exception as e:
                print(f"❌ Error closing Murf connection: {e}")
            finally:
                self.murf_websocket = None