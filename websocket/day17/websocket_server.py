# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
# from fastapi.responses import HTMLResponse
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn
# import json
# from datetime import datetime

# app = FastAPI()

# # Add CORS middleware - Very permissive for development
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, replace with specific domains
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)
#         print(f"Client connected. Total connections: {len(self.active_connections)}")

#     def disconnect(self, websocket: WebSocket):
#         if websocket in self.active_connections:
#             self.active_connections.remove(websocket)
#         print(f"Client disconnected. Total connections: {len(self.active_connections)}")

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         try:
#             await websocket.send_text(message)
#         except Exception as e:
#             print(f"Error sending message: {e}")
#             self.disconnect(websocket)

#     async def broadcast(self, message: str):
#         disconnected = []
#         for connection in self.active_connections:
#             try:
#                 await connection.send_text(message)
#             except:
#                 disconnected.append(connection)
        
#         # Remove disconnected clients
#         for conn in disconnected:
#             self.disconnect(conn)

# manager = ConnectionManager()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
    
#     # Send welcome message
#     welcome_msg = {
#         "type": "welcome",
#         "message": "🎉 Connected to WebSocket server!",
#         "timestamp": datetime.now().isoformat(),
#         "connection_id": str(id(websocket)),
#         "server": "FastAPI WebSocket Server v1.0"
#     }
#     await manager.send_personal_message(json.dumps(welcome_msg), websocket)
    
#     try:
#         while True:
#             # Receive message from client
#             data = await websocket.receive_text()
#             print(f"📨 Received message: {data}")
            
#             try:
#                 # Try to parse as JSON
#                 message_data = json.loads(data)
#                 message_type = message_data.get("type", "message")
#                 content = message_data.get("content", data)
#                 print(f"📋 Parsed JSON - Type: {message_type}, Content: {content}")
#             except json.JSONDecodeError:
#                 # If not JSON, treat as plain text
#                 message_type = "text"
#                 content = data
#                 print(f"📝 Plain text message: {content}")
            
#             # Create response message
#             response = {
#                 "type": "echo",
#                 "status": "success",
#                 "original_message": content,
#                 "message_type": message_type,
#                 "echo": f"🔄 Server echo: {content}",
#                 "timestamp": datetime.now().isoformat(),
#                 "connection_id": str(id(websocket)),
#                 "message_length": len(str(content))
#             }
            
#             # Echo back to the sender
#             await manager.send_personal_message(json.dumps(response, indent=2), websocket)
#             print(f"✅ Sent response back to client")
            
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         print("🔌 WebSocket connection closed normally")
#     except Exception as e:
#         print(f"❌ Error occurred: {e}")
#         manager.disconnect(websocket)

# # Add a simple REST endpoint to test CORS
# @app.get("/test")
# async def test_cors():
#     return {
#         "message": "CORS is working!",
#         "timestamp": datetime.now().isoformat(),
#         "active_connections": len(manager.active_connections)
#     }

# @app.get("/")
# async def get():
#     return HTMLResponse("""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>WebSocket Test - CORS Fixed</title>
#         <style>
#             body { font-family: Arial, sans-serif; margin: 20px; }
#             #messages { border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin: 10px 0; }
#             .message { margin: 5px 0; padding: 5px; background: #f0f0f0; border-radius: 3px; }
#             .sent { background: #e3f2fd; }
#             .received { background: #f3e5f5; }
#             input[type="text"] { width: 70%; padding: 8px; }
#             button { padding: 8px 15px; margin: 0 5px; }
#             .status { font-weight: bold; margin: 10px 0; }
#         </style>
#     </head>
#     <body>
#         <h1>🚀 WebSocket Test - CORS Fixed</h1>
#         <div id="status" class="status">Disconnected</div>
#         <div id="messages"></div>
#         <div>
#             <input type="text" id="messageText" placeholder="Type your message here...">
#             <button onclick="sendMessage()">Send Message</button>
#             <button onclick="connect()" id="connectBtn">Connect</button>
#             <button onclick="disconnect()" id="disconnectBtn">Disconnect</button>
#         </div>
#         <div style="margin-top: 10px;">
#             <button onclick="sendJsonMessage()">Send JSON Test</button>
#             <button onclick="clearMessages()">Clear Messages</button>
#         </div>

#         <script>
#             let ws = null;
#             const messages = document.getElementById('messages');
#             const status = document.getElementById('status');
#             const connectBtn = document.getElementById('connectBtn');
#             const disconnectBtn = document.getElementById('disconnectBtn');

#             function updateStatus(text, connected) {
#                 status.textContent = text;
#                 status.style.color = connected ? 'green' : 'red';
#                 connectBtn.disabled = connected;
#                 disconnectBtn.disabled = !connected;
#             }

#             function addMessage(message, type = 'received') {
#                 const div = document.createElement('div');
#                 div.className = `message ${type}`;
                
#                 try {
#                     const parsed = JSON.parse(message);
#                     div.innerHTML = `<strong>${type.toUpperCase()}:</strong> <pre>${JSON.stringify(parsed, null, 2)}</pre>`;
#                 } catch {
#                     div.innerHTML = `<strong>${type.toUpperCase()}:</strong> ${message}`;
#                 }
                
#                 messages.appendChild(div);
#                 messages.scrollTop = messages.scrollHeight;
#             }

#             function connect() {
#                 if (ws) return;
                
#                 updateStatus('Connecting...', false);
#                 ws = new WebSocket("ws://localhost:8000/ws");
                
#                 ws.onopen = function() {
#                     updateStatus('✅ Connected', true);
#                     addMessage('Connected to WebSocket server', 'system');
#                 };

#                 ws.onmessage = function(event) {
#                     addMessage(event.data, 'received');
#                 };

#                 ws.onclose = function() {
#                     updateStatus('❌ Disconnected', false);
#                     addMessage('Connection closed', 'system');
#                     ws = null;
#                 };

#                 ws.onerror = function(error) {
#                     updateStatus('❌ Connection Error', false);
#                     addMessage(`Error: ${error}`, 'error');
#                 };
#             }

#             function disconnect() {
#                 if (ws) {
#                     ws.close();
#                 }
#             }

#             function sendMessage() {
#                 const input = document.getElementById('messageText');
#                 if (ws && ws.readyState === WebSocket.OPEN && input.value.trim()) {
#                     ws.send(input.value);
#                     addMessage(input.value, 'sent');
#                     input.value = '';
#                 } else if (!ws || ws.readyState !== WebSocket.OPEN) {
#                     alert('Please connect to the WebSocket first!');
#                 }
#             }

#             function sendJsonMessage() {
#                 if (ws && ws.readyState === WebSocket.OPEN) {
#                     const jsonMsg = {
#                         type: "test_json",
#                         content: "This is a JSON test message",
#                         timestamp: new Date().toISOString(),
#                         user: "web_client",
#                         test_data: {
#                             number: Math.floor(Math.random() * 100),
#                             boolean: true,
#                             array: [1, 2, 3]
#                         }
#                     };
#                     const jsonString = JSON.stringify(jsonMsg);
#                     ws.send(jsonString);
#                     addMessage(jsonString, 'sent');
#                 } else {
#                     alert('Please connect to the WebSocket first!');
#                 }
#             }

#             function clearMessages() {
#                 messages.innerHTML = '';
#             }

#             // Send message on Enter key
#             document.getElementById('messageText').addEventListener('keypress', function(e) {
#                 if (e.key === 'Enter') {
#                     sendMessage();
#                 }
#             });

#             // Auto-connect on page load
#             window.onload = function() {
#                 updateStatus('Ready to connect', false);
#             };
#         </script>
#     </body>
#     </html>
#     """)

# # Health check endpoint
# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "active_connections": len(manager.active_connections),
#         "timestamp": datetime.now().isoformat(),
#         "server": "FastAPI WebSocket Server",
#         "cors_enabled": True
#     }

# if __name__ == "__main__":
#     print("🚀 Starting WebSocket server with CORS support...")
#     uvicorn.run(
#         "websocket_server:app",  # Replace with your actual filename
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info"
#     )



# import os
# import json
# import asyncio
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse
# from dotenv import load_dotenv

# # Import our custom AssemblyAI service
# from assembly_service import AssemblyAIStreamingClient

# load_dotenv()

# app = FastAPI()

# # Allow CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # HTML test page - EXACT copy from working GitHub implementation
# html = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>AssemblyAI Real-time Transcription</title>
#     <style>
#         body { font-family: Arial; padding: 20px; background: #f0f0f0; }
#         .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
#         button { padding: 15px 30px; font-size: 16px; margin: 10px; border: none; border-radius: 5px; cursor: pointer; }
#         .start { background: #4CAF50; color: white; }
#         .stop { background: #f44336; color: white; }
#         .status { padding: 15px; margin: 15px 0; border-radius: 5px; text-align: center; font-weight: bold; }
#         .ready { background: #d4edda; color: #155724; }
#         .recording { background: #fff3cd; color: #856404; }
#         .error { background: #f8d7da; color: #721c24; }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <h2>🎤 Real-time Audio Transcription</h2>
#         <div id="status" class="status ready">Ready to connect</div>
#         <button id="startBtn" class="start" onclick="start()">Start Recording</button>
#         <button id="stopBtn" class="stop" onclick="stop()" disabled>Stop Recording</button>
#         <p><strong>✨ Check your server terminal for live transcription results!</strong></p>
#         <p><em>Make sure to allow microphone access when prompted</em></p>
#     </div>

#     <script>
#         let ws, stream, mediaRecorder;
#         let recording = false;

#         function updateStatus(msg, type = 'ready') {
#             const status = document.getElementById('status');
#             status.textContent = msg;
#             status.className = `status ${type}`;
#         }

#         async function start() {
#             if (recording) return;
            
#             try {
#                 updateStatus('Connecting to server...', 'recording');
                
#                // Change this line in the HTML
#                 ws = new WebSocket('ws://localhost:8001/ws');
                
#                 ws.onopen = async () => {
#                     console.log('✅ Connected to server');
#                     updateStatus('Getting microphone access...', 'recording');
                    
#                     try {
#                         // Get microphone stream
#                         stream = await navigator.mediaDevices.getUserMedia({
#                             audio: {
#                                 sampleRate: 16000,
#                                 channelCount: 1,
#                                 echoCancellation: true,
#                                 noiseSuppression: true
#                             }
#                         });
                        
#                         console.log('🎤 Microphone access granted');
                        
#                         // Create MediaRecorder
#                         mediaRecorder = new MediaRecorder(stream, {
#                             mimeType: 'audio/webm',
#                         });
                        
#                         mediaRecorder.ondataavailable = (event) => {
#                             if (event.data.size > 0 && ws && ws.readyState === WebSocket.OPEN) {
#                                 console.log(`📤 Sending audio chunk: ${event.data.size} bytes`);
#                                 ws.send(event.data);
#                             }
#                         };
                        
#                         mediaRecorder.onerror = (event) => {
#                             console.error('❌ MediaRecorder error:', event.error);
#                         };
                        
#                         // Start recording with small time slices for real-time streaming
#                         mediaRecorder.start(100); // 100ms chunks
#                         recording = true;
                        
#                         updateStatus('🔴 Recording - Speak now!', 'recording');
#                         document.getElementById('startBtn').disabled = true;
#                         document.getElementById('stopBtn').disabled = false;
                        
#                     } catch (micError) {
#                         console.error('❌ Microphone error:', micError);
#                         updateStatus('Microphone access denied', 'error');
#                     }
#                 };

#                 ws.onmessage = (event) => {
#                     try {
#                         const data = JSON.parse(event.data);
#                         console.log('📨 Server response:', data);
#                     } catch (e) {
#                         console.log('📨 Server message:', event.data);
#                     }
#                 };
                
#                 ws.onerror = (error) => {
#                     console.error('❌ WebSocket error:', error);
#                     updateStatus('Connection error - Check server!', 'error');
#                 };
                
#                 ws.onclose = () => {
#                     console.log('🔌 WebSocket closed');
#                     if (recording) updateStatus('Connection lost', 'error');
#                 };
                
#             } catch (error) {
#                 console.error('❌ Error:', error);
#                 updateStatus('Error: ' + error.message, 'error');
#             }
#         }

#         function stop() {
#             if (!recording) return;
            
#             recording = false;
            
#             if (mediaRecorder && mediaRecorder.state !== 'inactive') {
#                 mediaRecorder.stop();
#             }
#             if (stream) {
#                 stream.getTracks().forEach(track => track.stop());
#             }
#             if (ws) {
#                 ws.close();
#             }
            
#             updateStatus('✅ Recording stopped', 'ready');
#             document.getElementById('startBtn').disabled = false;
#             document.getElementById('stopBtn').disabled = true;
#         }

#         window.addEventListener('beforeunload', stop);
#     </script>
# </body>
# </html>
# """

# @app.get("/")
# async def get():
#     return HTMLResponse(html)

# # EXACT WebSocket endpoint from the working GitHub implementation
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     print("WebSocket connection open")
    
#     # Initialize AssemblyAI client EXACTLY like the GitHub example
#     aaiClient = AssemblyAIStreamingClient(sample_rate=16000)
    
#     try:
#         while True:
#             data = await websocket.receive_bytes()
#             if not data:
#                 continue
            
#             # Stream audio to AssemblyAI
#             aaiClient.stream(data)
#             await websocket.send_json({"status": "transcribing audio"})
            
#     except WebSocketDisconnect:
#         print("WebSocket disconnected")
#     finally:
#         aaiClient.close()
#         print("AssemblyAI client disconnected")

# if __name__ == "__main__":
#     import uvicorn
#     print("="*60)
#     print("🚀 FASTAPI + ASSEMBLYAI STREAMING (GITHUB PATTERN)")
#     print("="*60)
#     print("📍 Server: http://localhost:8000")
#     print("📍 WebSocket: ws://localhost:8000/ws")
#     print("🎯 Using AssemblyAIStreamingClient pattern")
#     print("="*60)
#     print("💡 Open http://localhost:8000 to test!")
#     print("💡 Transcripts will appear in this terminal!")
#     print("="*60)
    
#     uvicorn.run(app, host="0.0.0.0", port=8001)






import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Import our custom AssemblyAI service
from assembly_service import AssemblyAIStreamingClient

load_dotenv()

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML test page - EXACT copy from working GitHub implementation
html = """
<!DOCTYPE html>
<html>
<head>
    <title>AssemblyAI Real-time Transcription</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #f0f0f0; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        button { padding: 15px 30px; font-size: 16px; margin: 10px; border: none; border-radius: 5px; cursor: pointer; }
        .start { background: #4CAF50; color: white; }
        .stop { background: #f44336; color: white; }
        .status { padding: 15px; margin: 15px 0; border-radius: 5px; text-align: center; font-weight: bold; }
        .ready { background: #d4edda; color: #155724; }
        .recording { background: #fff3cd; color: #856404; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎤 Real-time Audio Transcription</h2>
        <div id="status" class="status ready">Ready to connect</div>
        <button id="startBtn" class="start" onclick="start()">Start Recording</button>
        <button id="stopBtn" class="stop" onclick="stop()" disabled>Stop Recording</button>
        <p><strong>✨ Check your server terminal for live transcription results!</strong></p>
        <p><em>Make sure to allow microphone access when prompted</em></p>
    </div>

    <script>
        let ws, stream;
        let recording = false;

        function updateStatus(msg, type = 'ready') {
            const status = document.getElementById('status');
            status.textContent = msg;
            status.className = `status ${type}`;
        }

        async function start() {
            if (recording) return;
            
            try {
                updateStatus('Connecting to server...', 'recording');
                
                ws = new WebSocket('ws://localhost:8001/ws');
                
                ws.onopen = async () => {
                    console.log('✅ Connected to server');
                    updateStatus('Getting microphone access...', 'recording');
                    
                    try {
                        // Get microphone stream
                        stream = await navigator.mediaDevices.getUserMedia({
                            audio: {
                                sampleRate: 16000,
                                channelCount: 1,
                                echoCancellation: true,
                                noiseSuppression: true
                            }
                        });
                        
                        console.log('🎤 Microphone access granted');
                        
                        // Universal-Streaming needs PCM audio - use AudioContext
                        const audioContext = new AudioContext({ sampleRate: 16000 });
                        const source = audioContext.createMediaStreamSource(stream);
                        const processor = audioContext.createScriptProcessor(4096, 1, 1);
                        
                        processor.onaudioprocess = (event) => {
                            if (!recording || !ws || ws.readyState !== WebSocket.OPEN) return;
                            
                            const inputData = event.inputBuffer.getChannelData(0);
                            
                            // Convert to 16-bit PCM (little-endian) for Universal-Streaming
                            const pcmBuffer = new ArrayBuffer(inputData.length * 2);
                            const pcmView = new DataView(pcmBuffer);
                            
                            for (let i = 0; i < inputData.length; i++) {
                                // Clamp and convert to 16-bit PCM
                                const sample = Math.max(-1, Math.min(1, inputData[i]));
                                const pcmValue = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
                                pcmView.setInt16(i * 2, pcmValue, true); // little-endian
                            }
                            
                            console.log(`📤 Sending PCM audio: ${pcmBuffer.byteLength} bytes`);
                            ws.send(pcmBuffer);
                        };
                        
                        source.connect(processor);
                        processor.connect(audioContext.destination);
                        
                        // Store for cleanup
                        window.audioContext = audioContext;
                        window.processor = processor;
                        window.source = source;
                        recording = true;
                        
                        updateStatus('🔴 Recording - Speak now!', 'recording');
                        document.getElementById('startBtn').disabled = true;
                        document.getElementById('stopBtn').disabled = false;
                        
                    } catch (micError) {
                        console.error('❌ Microphone error:', micError);
                        updateStatus('Microphone access denied', 'error');
                    }
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        console.log('📨 Server response:', data);
                    } catch (e) {
                        console.log('📨 Server message:', event.data);
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('❌ WebSocket error:', error);
                    updateStatus('Connection error - Check server!', 'error');
                };
                
                ws.onclose = () => {
                    console.log('🔌 WebSocket closed');
                    if (recording) updateStatus('Connection lost', 'error');
                };
                
            } catch (error) {
                console.error('❌ Error:', error);
                updateStatus('Error: ' + error.message, 'error');
            }
        }

        function stop() {
            if (!recording) return;
            
            recording = false;
            
            // Clean up audio processing
            if (window.processor) {
                window.processor.disconnect();
                window.processor = null;
            }
            if (window.source) {
                window.source.disconnect(); 
                window.source = null;
            }
            if (window.audioContext) {
                window.audioContext.close();
                window.audioContext = null;
            }
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            if (ws) {
                ws.close();
            }
            
            updateStatus('✅ Recording stopped', 'ready');
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }

        window.addEventListener('beforeunload', stop);
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# EXACT WebSocket endpoint from the working GitHub implementation
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection open")
    
    # Initialize AssemblyAI client EXACTLY like the GitHub example
    aaiClient = AssemblyAIStreamingClient(sample_rate=16000)
    
    try:
        while True:
            data = await websocket.receive_bytes()
            if not data:
                continue
            
            # Stream audio to AssemblyAI
            aaiClient.stream(data)
            await websocket.send_json({"status": "transcribing audio"})
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        aaiClient.close()
        print("AssemblyAI client disconnected")

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🚀 FASTAPI + ASSEMBLYAI STREAMING (GITHUB PATTERN)")
    print("="*60)
    print("📍 Server: http://localhost:8001")
    print("📍 WebSocket: ws://localhost:8001/ws")
    print("🎯 Using AssemblyAIStreamingClient pattern")
    print("="*60)
    print("💡 Open http://localhost:8001 to test!")
    print("💡 Transcripts will appear in this terminal!")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)