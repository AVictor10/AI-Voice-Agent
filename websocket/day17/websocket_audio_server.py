# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse
# import uvicorn
# import os
# from datetime import datetime

# app = FastAPI()

# # Create audio directory
# os.makedirs("received_audio", exist_ok=True)

# @app.websocket("/ws/audio")
# async def websocket_audio_endpoint(websocket: WebSocket):
#     await websocket.accept()
    
#     # Create filename with timestamp
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     session_id = f"session_{len(os.listdir('received_audio')) + 1}"
#     filename = f"received_audio/audio_{session_id}_{timestamp}.wav"
    
#     print(f"\n🎤 AUDIO SESSION STARTED")
#     print(f"   Session ID: {session_id}")
#     print(f"   File: {filename}")
    
#     try:
#         with open(filename, "wb") as audio_file:
#             chunk_count = 0
#             total_bytes = 0
#             start_time = datetime.now()
            
#             while True:
#                 # Receive audio data
#                 data = await websocket.receive_bytes()
#                 chunk_count += 1
#                 total_bytes += len(data)
                
#                 # Save to file
#                 audio_file.write(data)
                
#                 # Show every chunk for first 10, then every 10th
#                 if chunk_count <= 10 or chunk_count % 10 == 0:
#                     print(f"🎵 Chunk #{chunk_count}: {len(data)} bytes (Total: {total_bytes:,} bytes)")
                
#     except WebSocketDisconnect:
#         duration = (datetime.now() - start_time).total_seconds()
#         file_size = os.path.getsize(filename)
        
#         print(f"\n🔴 AUDIO SESSION ENDED")
#         print(f"   Session ID: {session_id}")
#         print(f"   File saved: {filename}")
#         print(f"   Chunks received: {chunk_count}")
#         print(f"   Total bytes: {total_bytes:,}")
#         print(f"   File size: {file_size:,} bytes")
#         print(f"   Duration: {duration:.2f} seconds")
#         print(f"   Avg chunk size: {total_bytes//chunk_count if chunk_count > 0 else 0} bytes")
#         print("=" * 50)

# @app.get("/")
# async def get():
#     return HTMLResponse("""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Simple Audio WebSocket Test</title>
#         <style>
#             body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
#             button { padding: 15px 30px; margin: 10px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; }
#             .record { background: #f44336; color: white; }
#             .stop { background: #4caf50; color: white; }
#             #status { margin: 20px 0; font-weight: bold; font-size: 18px; }
#             .recording { color: #f44336; }
#             .stopped { color: #4caf50; }
#         </style>
#     </head>
#     <body>
#         <h1>🎤 Audio WebSocket with Live Stats</h1>
#         <div id="status">Ready to record</div>
#         <button onclick="startRecording()" id="startBtn" class="record">Start Recording</button>
#         <button onclick="stopRecording()" id="stopBtn" class="stop" disabled>Stop Recording</button>
        
#         <div style="margin-top: 30px; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto;">
#             <h3>📊 Live Stats:</h3>
#             <p><strong>Session ID:</strong> <span id="sessionId">-</span></p>
#             <p><strong>Chunks sent:</strong> <span id="chunkCount">0</span></p>
#             <p><strong>Total bytes:</strong> <span id="totalBytes">0</span></p>
#             <p><strong>Duration:</strong> <span id="duration">0s</span></p>
#         </div>

#         <script>
#             let ws = null;
#             let mediaRecorder = null;
#             let audioStream = null;
#             let chunkCount = 0;
#             let totalBytes = 0;
#             let startTime = null;
#             let sessionId = null;

#             async function startRecording() {
#                 try {
#                     // Get microphone
#                     audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    
#                     // Connect WebSocket
#                     ws = new WebSocket('ws://localhost:8000/ws/audio');
                    
#                     ws.onopen = function() {
#                         console.log('🔗 WebSocket connected');
#                         sessionId = `session_${Date.now()}`;
#                         document.getElementById('sessionId').textContent = sessionId;
                        
#                         // Start recording
#                         mediaRecorder = new MediaRecorder(audioStream);
                        
#                         mediaRecorder.ondataavailable = function(event) {
#                             if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
#                                 ws.send(event.data);
#                                 chunkCount++;
#                                 totalBytes += event.data.size;
                                
#                                 // Update UI stats
#                                 document.getElementById('chunkCount').textContent = chunkCount;
#                                 document.getElementById('totalBytes').textContent = totalBytes.toLocaleString();
                                
#                                 console.log(`📤 Sent chunk #${chunkCount}: ${event.data.size} bytes`);
#                             }
#                         };
                        
#                         mediaRecorder.start(100); // 100ms chunks
#                         startTime = Date.now();
                        
#                         // Update UI
#                         document.getElementById('status').textContent = '🔴 Recording...';
#                         document.getElementById('status').className = 'recording';
#                         document.getElementById('startBtn').disabled = true;
#                         document.getElementById('stopBtn').disabled = false;
                        
#                         // Start duration timer
#                         setInterval(updateDuration, 1000);
#                     };
                    
#                 } catch (error) {
#                     alert('Error: ' + error.message);
#                 }
#             }

#             function updateDuration() {
#                 if (startTime) {
#                     const duration = Math.floor((Date.now() - startTime) / 1000);
#                     document.getElementById('duration').textContent = duration + 's';
#                 }
#             }

#             function stopRecording() {
#                 if (mediaRecorder) {
#                     mediaRecorder.stop();
#                 }
                
#                 if (audioStream) {
#                     audioStream.getTracks().forEach(track => track.stop());
#                 }
                
#                 if (ws) {
#                     ws.close();
#                 }
                
#                 document.getElementById('status').textContent = '✅ Recording stopped';
#                 document.getElementById('status').className = 'stopped';
#                 document.getElementById('startBtn').disabled = false;
#                 document.getElementById('stopBtn').disabled = true;
                
#                 console.log(`🏁 Final stats: ${chunkCount} chunks, ${totalBytes.toLocaleString()} bytes`);
                
#                 // Reset for next recording
#                 chunkCount = 0;
#                 totalBytes = 0;
#                 startTime = null;
#             }
#         </script>
#     </body>
#     </html>
#     """)

# if __name__ == "__main__":
#     print("🎤 Simple Audio WebSocket Server")
#     print("📍 WebSocket: ws://localhost:8000/ws/audio")  
#     print("🌐 Test page: http://localhost:8000")
#     print("📁 Audio saved to: received_audio/")
    
#     uvicorn.run(app, host="127.0.0.1", port=8000)




# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse
# import uvicorn
# import os
# from datetime import datetime
# import asyncio
# import base64
# import assemblyai as aai
# import os
# from dotenv import load_dotenv
# import assemblyai as aai

# load_dotenv()

# # Load the special realtime key
# realtime_key = os.getenv("WEBSOCKET_ASSEMBLY_KEY")

# # Callback when transcription data is received
# async def on_data(transcript: aai.RealtimeTranscript):
#     if isinstance(transcript, aai.RealtimeFinalTranscript):
#         print(f"Final: {transcript.text}")
#     else:
#         print(f"Partial: {transcript.text}")

# # Create the realtime transcriber with this key
# transcriber = aai.RealtimeTranscriber(
#     sample_rate=16000,
#     on_data=on_data,
#     on_error=on_error
# )



# app = FastAPI()

# # Create audio directory
# os.makedirs("received_audio", exist_ok=True)


# @app.websocket("/ws/audio")
# async def websocket_audio_endpoint(websocket: WebSocket):
#     await websocket.accept()

#     # Create filename with timestamp
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     session_id = f"session_{len(os.listdir('received_audio')) + 1}"
#     filename = f"received_audio/audio_{session_id}_{timestamp}.wav"

#     print(f"\n🎤 AUDIO SESSION STARTED")
#     print(f"   Session ID: {session_id}")
#     print(f"   File: {filename}")

#     # AssemblyAI Realtime connection
#     transcriber = aai.RealtimeTranscriber(
#         sample_rate=16000,
#         on_data=lambda transcript: (
#             print(f"📝 Transcript: {transcript.text}")
#             if transcript.text
#             else None
#         ),
#         on_error=lambda err: print(f"❌ AAI error: {err}"),
#     )

#     await transcriber.connect()

#     try:
#         with open(filename, "wb") as audio_file:
#             chunk_count = 0
#             total_bytes = 0
#             start_time = datetime.now()

#             while True:
#                 # Receive audio data
#                 data = await websocket.receive_bytes()
#                 chunk_count += 1
#                 total_bytes += len(data)

#                 # Save raw bytes to file
#                 audio_file.write(data)

#                 # Forward audio to AssemblyAI (base64 encode)
#                 await transcriber.stream(base64.b64encode(data).decode("utf-8"))

#                 # Show every chunk for first 10, then every 10th
#                 if chunk_count <= 10 or chunk_count % 10 == 0:
#                     print(f"🎵 Chunk #{chunk_count}: {len(data)} bytes (Total: {total_bytes:,} bytes)")

#     except WebSocketDisconnect:
#         await transcriber.close()

#         duration = (datetime.now() - start_time).total_seconds()
#         file_size = os.path.getsize(filename)

#         print(f"\n🔴 AUDIO SESSION ENDED")
#         print(f"   Session ID: {session_id}")
#         print(f"   File saved: {filename}")
#         print(f"   Chunks received: {chunk_count}")
#         print(f"   Total bytes: {total_bytes:,}")
#         print(f"   File size: {file_size:,} bytes")
#         print(f"   Duration: {duration:.2f} seconds")
#         print(f"   Avg chunk size: {total_bytes//chunk_count if chunk_count > 0 else 0} bytes")
#         print("=" * 50)


# @app.get("/")
# async def get():
#     return HTMLResponse(""" 
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Simple Audio WebSocket Test</title>
#         <style>
#             body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
#             button { padding: 15px 30px; margin: 10px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; }
#             .record { background: #f44336; color: white; }
#             .stop { background: #4caf50; color: white; }
#             #status { margin: 20px 0; font-weight: bold; font-size: 18px; }
#             .recording { color: #f44336; }
#             .stopped { color: #4caf50; }
#         </style>
#     </head>
#     <body>
#         <h1>🎤 Audio WebSocket with Live Stats</h1>
#         <div id="status">Ready to record</div>
#         <button onclick="startRecording()" id="startBtn" class="record">Start Recording</button>
#         <button onclick="stopRecording()" id="stopBtn" class="stop" disabled>Stop Recording</button>
        
#         <div style="margin-top: 30px; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto;">
#             <h3>📊 Live Stats:</h3>
#             <p><strong>Session ID:</strong> <span id="sessionId">-</span></p>
#             <p><strong>Chunks sent:</strong> <span id="chunkCount">0</span></p>
#             <p><strong>Total bytes:</strong> <span id="totalBytes">0</span></p>
#             <p><strong>Duration:</strong> <span id="duration">0s</span></p>
#         </div>

#         <script>
#             let ws = null;
#             let mediaRecorder = null;
#             let audioStream = null;
#             let chunkCount = 0;
#             let totalBytes = 0;
#             let startTime = null;
#             let sessionId = null;

#             async function startRecording() {
#                 try {
#                     // Get microphone
#                     audioStream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, sampleRate: 16000 } });
                    
#                     // Connect WebSocket
#                     ws = new WebSocket('ws://localhost:8000/ws/audio');
                    
#                     ws.onopen = function() {
#                         console.log('🔗 WebSocket connected');
#                         sessionId = `session_${Date.now()}`;
#                         document.getElementById('sessionId').textContent = sessionId;
                        
#                         // Start recording PCM audio
#                         mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm;codecs=pcm' });
                        
#                         mediaRecorder.ondataavailable = function(event) {
#                             if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
#                                 event.data.arrayBuffer().then(buffer => {
#                                     ws.send(buffer);
#                                     chunkCount++;
#                                     totalBytes += buffer.byteLength;
#                                     document.getElementById('chunkCount').textContent = chunkCount;
#                                     document.getElementById('totalBytes').textContent = totalBytes.toLocaleString();
#                                     console.log(`📤 Sent chunk #${chunkCount}: ${buffer.byteLength} bytes`);
#                                 });
#                             }
#                         };
                        
#                         mediaRecorder.start(100); // 100ms chunks
#                         startTime = Date.now();
                        
#                         document.getElementById('status').textContent = '🔴 Recording...';
#                         document.getElementById('status').className = 'recording';
#                         document.getElementById('startBtn').disabled = true;
#                         document.getElementById('stopBtn').disabled = false;
                        
#                         setInterval(updateDuration, 1000);
#                     };
                    
#                 } catch (error) {
#                     alert('Error: ' + error.message);
#                 }
#             }

#             function updateDuration() {
#                 if (startTime) {
#                     const duration = Math.floor((Date.now() - startTime) / 1000);
#                     document.getElementById('duration').textContent = duration + 's';
#                 }
#             }

#             function stopRecording() {
#                 if (mediaRecorder) mediaRecorder.stop();
#                 if (audioStream) audioStream.getTracks().forEach(track => track.stop());
#                 if (ws) ws.close();
                
#                 document.getElementById('status').textContent = '✅ Recording stopped';
#                 document.getElementById('status').className = 'stopped';
#                 document.getElementById('startBtn').disabled = false;
#                 document.getElementById('stopBtn').disabled = true;
                
#                 console.log(`🏁 Final stats: ${chunkCount} chunks, ${totalBytes.toLocaleString()} bytes`);
                
#                 chunkCount = 0;
#                 totalBytes = 0;
#                 startTime = null;
#             }
#         </script>
#     </body>
#     </html>
#     """)


# if __name__ == "__main__":
#     print("🎤 Simple Audio WebSocket Server with AssemblyAI Transcription")
#     print("📍 WebSocket: ws://localhost:8000/ws/audio")
#     print("🌐 Test page: http://localhost:8000")
#     print("📁 Audio saved to: received_audio/")
#     uvicorn.run(app, host="127.0.0.1", port=8000)



# Simple WebSocket Audio Server
# pip install fastapi uvicorn websockets assemblyai

import asyncio
import websockets
import assemblyai as aai
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key - try both possible names
ASSEMBLYAI_API_KEY = os.getenv("WEBSOCKET_ASSEMBLY_KEY") or os.getenv("ASSEMBLYAI_API_KEY")

if not ASSEMBLYAI_API_KEY:
    print("❌ ERROR: API key not found!")
    print("Add to your .env file: WEBSOCKET_ASSEMBLY_KEY=your_api_key_here")
    exit(1)

print(f"🔑 Using API key: ...{ASSEMBLYAI_API_KEY[-8:]}")
aai.settings.api_key = ASSEMBLYAI_API_KEY

class TerminalTranscriber:
    def __init__(self):
        self.transcriber = None
        self.websocket = None
        
    def start(self, websocket):
        self.websocket = websocket
        
        try:
            self.transcriber = aai.RealtimeTranscriber(
                sample_rate=16000,
                on_data=self.on_transcript,
                on_error=self.on_error,
            )
            
            self.transcriber.connect()
            print("✅ Connected to AssemblyAI")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
        
    def on_transcript(self, transcript):
        if not transcript.text:
            return
            
        # This is what you see in terminal!
        if transcript.message_type == aai.RealtimeTranscriptType.FinalTranscript:
            print(f"🟢 FINAL: {transcript.text}")
        else:
            print(f"🟡 PARTIAL: {transcript.text}")
    
    def on_error(self, error):
        print(f"❌ Error: {error}")
            
    def stream_audio(self, audio_data):
        if self.transcriber:
            self.transcriber.stream(audio_data)
            
    def close(self):
        if self.transcriber:
            self.transcriber.close()
            print("🔌 Transcriber closed")

async def handle_client(websocket, path):
    print("🎧 Client connected")
    
    transcriber = TerminalTranscriber()
    
    if not transcriber.start(websocket):
        await websocket.close()
        return
    
    try:
        # Send ready signal
        await websocket.send(json.dumps({"type": "ready"}))
        
        # Process audio data
        async for message in websocket:
            if isinstance(message, bytes):
                transcriber.stream_audio(message)
                
    except websockets.exceptions.ConnectionClosed:
        print("🔌 Client disconnected")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        transcriber.close()

async def main():
    print("="*50)
    print("🚀 WEBSOCKET AUDIO TRANSCRIBER")
    print("="*50)
    print("📍 Server: ws://localhost:8765")
    print(f"🎯 API Key loaded: {'✅ Yes' if ASSEMBLYAI_API_KEY else '❌ No'}")
    print("="*50)
    print("👂 Listening for connections...")
    
    try:
        async with websockets.serve(handle_client, "localhost", 8765):
            await asyncio.Future()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())