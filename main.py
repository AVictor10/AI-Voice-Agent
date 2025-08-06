from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from murf import Murf
from dotenv import load_dotenv
from fastapi import UploadFile, File
from pathlib import Path
import os

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
    file_path = UPLOAD_DIR / file.filename
    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }
