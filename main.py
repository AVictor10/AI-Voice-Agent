from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from murf import Murf
from dotenv import load_dotenv
from fastapi import UploadFile, File
from pathlib import Path
from datetime import datetime
import assemblyai as aai
import os
import uuid

load_dotenv()

app = FastAPI()

# Mount static files (HTML, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request body
class TextRequest(BaseModel):
    text: str

# Initialize Murf SDK
MURF_API_KEY = os.getenv("MURF_API_KEY")
client = Murf(api_key=MURF_API_KEY)

@app.post("/generate-audio/")
async def generate_audio(request: TextRequest):
    try:
        audio_res = client.text_to_speech.generate(
            text=request.text,
            voice_id="en-US-terrell"
        )
        return {"audio_url": audio_res.audio_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    extension = file.filename.split(".")[-1]
    new_filename = f"audio_{timestamp}_{unique_id}.{extension}"

    file_path = UPLOAD_DIR / new_filename
    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "filename": new_filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

#Transcribe File Logic

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

@app.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...)):
    try:
        # Read contents of the uploaded file
        audio_bytes = await file.read()

        # Use AssemblyAI SDK to transcribe directly from bytes
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_bytes)

        if transcript.status == "error":
            raise RuntimeError(f"Transcription failed: {transcript.error}")

        return {"transcript": transcript.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))