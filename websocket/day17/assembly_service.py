import os
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

        self.sample_rate = sample_rate
        self.client = None
        self._setup_client()

    def _setup_client(self):
        """Setup the Universal-Streaming client"""
        
        def on_begin(client, event: BeginEvent):
            print(f"✅ Universal-Streaming session started: {event.id}")

        def on_turn(client, event: TurnEvent):
            """Handle transcription turns - this is where transcripts come through"""
            if event.transcript:
                if event.end_of_turn:
                    print(f"🟢 FINAL: {event.transcript}")
                else:
                    print(f"🟡 PARTIAL: {event.transcript}")

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
            
            # Connect to AssemblyAI Universal-Streaming
            self.client.connect(
                StreamingParameters(
                    sample_rate=self.sample_rate,
                    formatted_finals=False,  # Set to True if you want formatted text
                )
            )
            print("🔗 Connected to AssemblyAI Universal-Streaming")
            
        except Exception as e:
            print(f"❌ Failed to setup Universal-Streaming client: {e}")
            raise e

    def stream(self, audio_chunk: bytes):
        """Stream audio data to AssemblyAI Universal-Streaming"""
        if self.client:
            try:
                self.client.stream(audio_chunk)
            except Exception as e:
                print(f"❌ Error streaming audio: {e}")

    def close(self):
        """Close the connection to AssemblyAI"""
        if self.client:
            try:
                self.client.disconnect()
                print("🔌 AssemblyAI Universal-Streaming connection closed")
            except Exception as e:
                print(f"❌ Error closing client: {e}")
            finally:
                self.client = None