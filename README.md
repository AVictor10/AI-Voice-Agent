# 🎙 AI Voice Agent — 30 Days Challenge

An **end-to-end AI voice assistant** built using FastAPI, modern frontend technologies, and multiple AI APIs.  
The bot can **listen**, **understand**, **remember conversations**, and **speak back** — just like a human!

---
✨ ## Features

🎙️ Voice Input – Record speech and send it directly to the AI for processing.

🧠 LLM Integration – Uses Google Gemini to generate intelligent, context-aware responses.

🗣️ Text-to-Speech Output – Murf API converts LLM responses into natural-sounding speech.

📝 Speech-to-Text – AssemblyAI transcribes user audio for the LLM to process.

💬 Conversation Memory – Chat history stored by session to maintain context across interactions.

⚡ Real-time Interaction – Instant query-response loop for smooth voice conversations.

🌐 Full-Stack Architecture – FastAPI backend with HTML/CSS/JS frontend.

🛠️ Modular Design – Clean separation of logic for easy scaling and feature addition.

## 📅 Progress Timeline

| Day  | 🚀 Milestone | 📝 Details |
|------|-------------|-----------|
| **Day 1** | 📂 **Project Setup** | Initialized **FastAPI** backend + **HTML/CSS/JS** frontend. Set up environment variables & folder structure. |
| **Day 2** | 🌐 **Static Files & UI** | Served static assets via FastAPI. Built minimal UI to send requests to backend endpoints. |
| **Day 3** | 🎙 **Audio Upload Endpoint** | Created a file upload API to handle incoming audio files from the frontend. |
| **Day 4** | 🎛 **Frontend Recording** | Implemented **MediaRecorder API** to record audio in browser, send as blob to backend. |
| **Day 5** | 🗣 **Speech-to-Text (STT)** | Connected **AssemblyAI API** to transcribe uploaded audio. Tested full upload → transcription pipeline. |
| **Day 6** | ⚡ **Optimized STT Flow** | Removed local file saves; enabled direct streaming to AssemblyAI for faster results. |
| **Day 7** | 🔊 **Text-to-Speech (TTS)** | Integrated **Murf API** to convert AI text responses into realistic speech. |
| **Day 8** | 🤖 **LLM Integration** | Added **Gemini API** to `/llm/query` for AI-powered text-based queries & responses. |
| **Day 9** | 🎤 **Audio-to-Audio LLM** | Extended `/llm/query` to handle audio: Speech → STT → LLM → TTS → Playback. |
| **Day 10** | 💬 **Chat History & Memory** | Implemented in-memory datastore with session IDs so conversations retain context. |
| **Day 11** | 🔄 **Continuous Conversation** | Bot now automatically restarts recording after its response finishes playing. |
| **Day 12** | 🎨 **UI & Performance Polish** | Upgraded frontend design, fixed autoplay bugs, and reduced response latency. |
| **Day 13** | 🏆 **Refined UX & Session Control** | Improved natural flow, better session management, and smoother AI-human interaction. |

---

## 🛠 Technologies Used

### **Languages & Frameworks**
- 🐍 **Python 3.10+**
- ⚡ **FastAPI** (Backend)
- 🌐 **HTML5**, **CSS3**, **JavaScript (ES6)** (Frontend)

### **APIs & AI Services**
- 🗣 **AssemblyAI** — Speech-to-Text (STT)
- 🔊 **Murf AI** — Text-to-Speech (TTS)
- 🤖 **Google Gemini API** — Large Language Model (LLM)

### **Tools & Libraries**
- 📦 `requests` — API calls
- 🎯 `pydantic` — Data validation
- 🔄 `uvicorn` — ASGI server for FastAPI

---

## 🏗 Architecture Overview

```plaintext
🎤 User Speaks
    ↓
🎙 Browser Records Audio (MediaRecorder API)
    ↓
📡 Send to FastAPI Endpoint (/agent/chat/{session_id})
    ↓
🗣 AssemblyAI → Transcribe Audio
    ↓
🤖 Gemini API → Generate AI Response
    ↓
🔊 Murf API → Convert Text to Speech
    ↓
🎧 Browser Plays AI Response
    ↓
🔁 Continue Conversation with Memory
