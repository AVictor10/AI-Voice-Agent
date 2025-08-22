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
#         let ws, stream;
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
                        
#                         // Universal-Streaming needs PCM audio - use AudioContext
#                         const audioContext = new AudioContext({ sampleRate: 16000 });
#                         const source = audioContext.createMediaStreamSource(stream);
#                         const processor = audioContext.createScriptProcessor(4096, 1, 1);
                        
#                         processor.onaudioprocess = (event) => {
#                             if (!recording || !ws || ws.readyState !== WebSocket.OPEN) return;
                            
#                             const inputData = event.inputBuffer.getChannelData(0);
                            
#                             // Convert to 16-bit PCM (little-endian) for Universal-Streaming
#                             const pcmBuffer = new ArrayBuffer(inputData.length * 2);
#                             const pcmView = new DataView(pcmBuffer);
                            
#                             for (let i = 0; i < inputData.length; i++) {
#                                 // Clamp and convert to 16-bit PCM
#                                 const sample = Math.max(-1, Math.min(1, inputData[i]));
#                                 const pcmValue = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
#                                 pcmView.setInt16(i * 2, pcmValue, true); // little-endian
#                             }
                            
#                             console.log(`📤 Sending PCM audio: ${pcmBuffer.byteLength} bytes`);
#                             ws.send(pcmBuffer);
#                         };
                        
#                         source.connect(processor);
#                         processor.connect(audioContext.destination);
                        
#                         // Store for cleanup
#                         window.audioContext = audioContext;
#                         window.processor = processor;
#                         window.source = source;
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
            
#             // Clean up audio processing
#             if (window.processor) {
#                 window.processor.disconnect();
#                 window.processor = null;
#             }
#             if (window.source) {
#                 window.source.disconnect(); 
#                 window.source = null;
#             }
#             if (window.audioContext) {
#                 window.audioContext.close();
#                 window.audioContext = null;
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
#     print("📍 Server: http://localhost:8001")
#     print("📍 WebSocket: ws://localhost:8001/ws")
#     print("🎯 Using AssemblyAIStreamingClient pattern")
#     print("="*60)
#     print("💡 Open http://localhost:8001 to test!")
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

# HTML with Turn Detection UI
html = """
<!DOCTYPE html>
<html>
<head>
    <title>AssemblyAI Turn Detection Demo</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            padding: 20px; 
            background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%);
            min-height: 100vh;
            margin: 0;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h2 { 
            text-align: center; 
            color: #333; 
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        button { 
            padding: 15px 30px; 
            font-size: 18px; 
            margin: 10px; 
            border: none; 
            border-radius: 10px; 
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .start { 
            background: linear-gradient(45deg, #4CAF50, #45a049); 
            color: white; 
        }
        .start:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(76,175,80,0.4); }
        .stop { 
            background: linear-gradient(45deg, #f44336, #da190b); 
            color: white; 
        }
        .stop:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(244,67,54,0.4); }
        .status { 
            padding: 20px; 
            margin: 20px 0; 
            border-radius: 15px; 
            text-align: center; 
            font-weight: bold;
            font-size: 18px;
        }
        .ready { background: linear-gradient(45deg, #d4edda, #c3e6cb); color: #155724; }
        .recording { background: linear-gradient(45deg, #fff3cd, #ffeaa7); color: #856404; }
        .error { background: linear-gradient(45deg, #f8d7da, #f5c6cb); color: #721c24; }
        .speaking { background: linear-gradient(45deg, #cce5ff, #99d6ff); color: #004085; }
        
        .transcript-section {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
            border: 2px solid #e9ecef;
        }
        
        .transcript-item {
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #007bff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease-out;
        }
        
        .transcript-final {
            border-left-color: #28a745;
            background: linear-gradient(45deg, #d4f6dd, #c8f5d1);
        }
        
        .transcript-partial {
            border-left-color: #ffc107;
            background: linear-gradient(45deg, #fff8dc, #fffacd);
            opacity: 0.8;
        }
        
        .turn-indicator {
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .transcript-text {
            font-size: 16px;
            line-height: 1.5;
            color: #333;
        }
        
        @keyframes slideIn {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .controls {
            text-align: center;
            margin: 30px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎤 AssemblyAI Turn Detection Demo</h2>
        
        <div id="status" class="status ready">Ready to start turn detection</div>
        
        <div class="controls">
            <button id="startBtn" class="start" onclick="start()">🎙️ Start Recording</button>
            <button id="stopBtn" class="stop" onclick="stop()" disabled>⏹️ Stop Recording</button>
        </div>
        
        <div class="transcript-section">
            <h3>🔄 Live Turn Detection</h3>
            <div id="transcriptContainer">
                <p style="text-align: center; color: #666; font-style: italic;">
                    Transcripts will appear here when you finish speaking (turn detection)...
                </p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <p><strong>✨ Speak clearly and pause - turn detection will trigger!</strong></p>
            <p><em>Make sure to allow microphone access when prompted</em></p>
        </div>
    </div>

    <script>
        let ws, stream;
        let recording = false;
        let turnCount = 0;

        function updateStatus(msg, type = 'ready') {
            const status = document.getElementById('status');
            status.textContent = msg;
            status.className = `status ${type}`;
        }
        
        function addTranscript(data) {
            const container = document.getElementById('transcriptContainer');
            
            // Clear placeholder text on first transcript
            if (container.children.length === 1 && container.children[0].tagName === 'P') {
                container.innerHTML = '';
            }
            
            const transcriptDiv = document.createElement('div');
            
            if (data.type === 'end_of_turn') {
                // Final transcript - turn ended
                turnCount++;
                transcriptDiv.className = 'transcript-item transcript-final';
                transcriptDiv.innerHTML = `
                    <div class="turn-indicator">🎯 Turn ${turnCount} Completed (Confidence: ${(data.confidence * 100).toFixed(1)}%)</div>
                    <div class="transcript-text">${data.transcript}</div>
                `;
                
                // Update status to show turn detection
                updateStatus('🎯 Turn detected! User finished speaking.', 'ready');
                
                // Auto-clear status after 3 seconds
                setTimeout(() => {
                    if (recording) updateStatus('🔴 Recording - Speak and pause for turn detection', 'recording');
                }, 3000);
                
            } else if (data.type === 'partial_transcript') {
                // Partial transcript - user still speaking
                // Remove previous partial if exists
                const existingPartial = container.querySelector('.transcript-partial');
                if (existingPartial) {
                    existingPartial.remove();
                }
                
                transcriptDiv.className = 'transcript-item transcript-partial';
                transcriptDiv.innerHTML = `
                    <div class="turn-indicator">🗣️ Speaking... (Turn in progress)</div>
                    <div class="transcript-text">${data.transcript}</div>
                `;
                
                updateStatus('🗣️ User is speaking...', 'speaking');
            }
            
            container.appendChild(transcriptDiv);
            container.scrollTop = container.scrollHeight;
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
                                noiseSuppression: true,
                                autoGainControl: true
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
                            
                            ws.send(pcmBuffer);
                        };
                        
                        source.connect(processor);
                        processor.connect(audioContext.destination);
                        
                        // Store for cleanup
                        window.audioContext = audioContext;
                        window.processor = processor;
                        window.source = source;
                        
                        recording = true;
                        updateStatus('🔴 Recording - Speak and pause for turn detection', 'recording');
                        
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
                        console.log('📨 Received:', data);
                        
                        // Handle turn detection messages
                        if (data.type === 'end_of_turn' || data.type === 'partial_transcript') {
                            addTranscript(data);
                        }
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

# WebSocket endpoint with turn detection support
# WebSocket endpoint with turn detection support
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection open")
    
    # Initialize AssemblyAI client
    aaiClient = AssemblyAIStreamingClient(sample_rate=16000)
    
    # 🔥 KEY: Set WebSocket reference for turn detection callbacks
    aaiClient.set_websocket(websocket)
    
    try:
        while True:
            # Check for pending messages from AssemblyAI and send them
            await aaiClient.process_pending_messages()
            
            # Receive audio data with timeout to allow message processing
            try:
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=0.1)
                if data:
                    # Stream audio to AssemblyAI (turn detection happens automatically)
                    aaiClient.stream(data)
            except asyncio.TimeoutError:
                # Timeout is normal - allows us to process pending messages
                continue
            except Exception as e:
                print(f"❌ Error receiving data: {e}")
                break
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"❌ Error in websocket: {e}")
    finally:
        aaiClient.close()
        print("AssemblyAI client disconnected")

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🎯 ASSEMBLYAI TURN DETECTION DEMO")
    print("="*60)
    print("📍 Server: http://localhost:8001")
    print("📍 WebSocket: ws://localhost:8001/ws")
    print("🎯 Turn Detection: ENABLED")
    print("🎤 Speak and pause to trigger turn detection!")
    print("="*60)
    print("💡 Open http://localhost:8001 to test!")
    print("💡 Turn detection will appear in UI and terminal!")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)