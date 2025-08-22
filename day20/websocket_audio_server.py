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