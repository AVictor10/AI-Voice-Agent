// Global variables
let mediaRecorder;
let audioChunks = [];
let recordedBlob;
let currentSessionId = '';
let autoRecordEnabled = false;
let isWaitingForResponse = false;

// Initialize session management when page loads
document.addEventListener("DOMContentLoaded", () => {
  initializeSession();
  setupEventListeners();
  setupLegacyEventListeners();
});

// ==================== SESSION MANAGEMENT ====================

function initializeSession() {
  // Get session ID from URL params or generate new one
  const urlParams = new URLSearchParams(window.location.search);
  const sessionFromUrl = urlParams.get('session');
  
  if (sessionFromUrl) {
    currentSessionId = sessionFromUrl;
  } else {
    currentSessionId = generateSessionId();
    // Update URL with session ID
    const newUrl = `${window.location.pathname}?session=${currentSessionId}`;
    window.history.replaceState({}, '', newUrl);
  }
  
  document.getElementById('current-session').textContent = currentSessionId;
  loadSessionHistory();
}

function generateSessionId() {
  return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

function updateSessionInUrl(sessionId) {
  const newUrl = `${window.location.pathname}?session=${sessionId}`;
  window.history.pushState({}, '', newUrl);
}

async function loadSessionHistory() {
  try {
    const response = await fetch(`http://127.0.0.1:8000/agent/history/${currentSessionId}`);
    const data = await response.json();
    
    if (data.status === 'success') {
      updateSessionInfo(data.conversation_turns, data.message_count);
      displayChatHistory(data.history);
    }
  } catch (error) {
    console.error('Failed to load session history:', error);
  }
}

function updateSessionInfo(turns, messages) {
  document.getElementById('conversation-turns').textContent = turns;
  document.getElementById('total-messages').textContent = messages;
}

function displayChatHistory(history) {
  const historyContainer = document.getElementById('history-messages');
  historyContainer.innerHTML = '';
  
  history.forEach(message => {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${message.role}`;
    
    const time = new Date(message.timestamp * 1000).toLocaleTimeString();
    messageDiv.innerHTML = `
      <div class="message-content">${message.content}</div>
      <div class="message-time">${time}</div>
    `;
    
    historyContainer.appendChild(messageDiv);
  });
  
  // Scroll to bottom
  historyContainer.scrollTop = historyContainer.scrollHeight;
}

// ==================== EVENT LISTENERS SETUP ====================

function setupEventListeners() {
  // Session management
  document.getElementById('new-session-btn').addEventListener('click', createNewSession);
  document.getElementById('clear-history-btn').addEventListener('click', clearCurrentSession);
  document.getElementById('load-session-btn').addEventListener('click', loadCustomSession);
  
  // Recording controls
  document.getElementById('start-recording').addEventListener('click', startRecording);
  document.getElementById('stop-recording').addEventListener('click', stopRecording);
  document.getElementById('chat-conversation').addEventListener('click', sendToAI);
  
  // Auto-record toggle (click on indicator)
  document.getElementById('auto-record-status').addEventListener('click', toggleAutoRecord);
}

// ==================== SESSION CONTROL FUNCTIONS ====================

function createNewSession() {
  currentSessionId = generateSessionId();
  document.getElementById('current-session').textContent = currentSessionId;
  updateSessionInUrl(currentSessionId);
  updateSessionInfo(0, 0);
  document.getElementById('history-messages').innerHTML = '';
  updateStatus('🆕 New session created!', 'success');
}

async function clearCurrentSession() {
  try {
    const response = await fetch(`http://127.0.0.1:8000/agent/history/${currentSessionId}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      updateSessionInfo(0, 0);
      document.getElementById('history-messages').innerHTML = '';
      updateStatus('🗑️ Session history cleared!', 'success');
    }
  } catch (error) {
    console.error('Failed to clear session:', error);
    updateStatus('❌ Failed to clear session', 'error');
  }
}

function loadCustomSession() {
  const customSessionInput = document.getElementById('custom-session-input');
  const sessionId = customSessionInput.value.trim();
  
  if (!sessionId) {
    alert('Please enter a session ID');
    return;
  }
  
  currentSessionId = sessionId;
  document.getElementById('current-session').textContent = currentSessionId;
  updateSessionInUrl(currentSessionId);
  customSessionInput.value = '';
  loadSessionHistory();
  updateStatus('📂 Session loaded!', 'success');
}

function toggleAutoRecord() {
  autoRecordEnabled = !autoRecordEnabled;
  const indicator = document.getElementById('auto-record-status');
  indicator.textContent = `Auto-record: ${autoRecordEnabled ? 'ON' : 'OFF'}`;
  indicator.style.background = autoRecordEnabled 
    ? 'linear-gradient(135deg, #20bf6b 0%, #26d0ce 100%)'
    : 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)';
}

// ==================== RECORDING FUNCTIONS ====================

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      recordedBlob = new Blob(audioChunks, { type: "audio/webm" });
      const audioUrl = URL.createObjectURL(recordedBlob);
      document.getElementById('recorded-audio').src = audioUrl;
      
      // Enable send button
      document.getElementById('chat-conversation').disabled = false;
      
      updateStatus('🎤 Recording complete! Ready to send to AI.', 'success');
    };

    mediaRecorder.start();
    
    // Update UI
    document.getElementById('start-recording').disabled = true;
    document.getElementById('start-recording').classList.add('recording');
    document.getElementById('stop-recording').disabled = false;
    
    updateStatus('🔴 Recording...', 'processing');
    
  } catch (error) {
    console.error('Error starting recording:', error);
    updateStatus('❌ Failed to start recording', 'error');
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    
    // Update UI
    document.getElementById('start-recording').disabled = false;
    document.getElementById('start-recording').classList.remove('recording');
    document.getElementById('stop-recording').disabled = true;
    
    // Stop all tracks to free up microphone
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
  }
}

// ==================== AI CONVERSATION FUNCTIONS ====================

async function sendToAI() {
  if (!recordedBlob) {
    alert("Please record something first!");
    return;
  }

  const formData = new FormData();
  formData.append("audio_file", recordedBlob, "recording.webm");
  
  // Add voice selection
  const voiceSelect = document.getElementById("voiceSelect");
  if (voiceSelect) {
    formData.append("voiceId", voiceSelect.value);
  }

  updateStatus('🤖 Processing with AI...', 'processing');
  isWaitingForResponse = true;
  
  // Disable send button while processing
  document.getElementById('chat-conversation').disabled = true;

  try {
    const response = await fetch(`http://127.0.0.1:8000/agent/chat/${currentSessionId}`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();

    if (result.error) {
      throw new Error(result.error);
    }

    // Update session info
    updateSessionInfo(result.conversation_turns, result.conversation_length);

    // Display the conversation
    updateStatus(`✅ AI Response: "${result.response.substring(0, 100)}..."`, 'success');

    // Play the AI response audio
    if (result.audio_url) {
      const aiAudio = document.getElementById('ai-response-audio');
      aiAudio.src = result.audio_url;
      
      // Play the response
      await aiAudio.play();
      
      // If multiple chunks, play them sequentially
      if (result.audio_urls && result.audio_urls.length > 1) {
        await playAudioSequentially(result.audio_urls);
      }
      
      // Set up auto-record after audio finishes
      if (autoRecordEnabled) {
        aiAudio.onended = () => {
          setTimeout(() => {
            if (!isWaitingForResponse) return; // Safety check
            startAutoRecord();
          }, 1000); // 1 second delay after AI response ends
        };
      }
    }

    // Refresh chat history
    loadSessionHistory();
    
    isWaitingForResponse = false;

  } catch (error) {
    console.error("Error:", error);
    updateStatus(`❌ AI processing failed: ${error.message}`, 'error');
    isWaitingForResponse = false;
  }
}

async function startAutoRecord() {
  if (autoRecordEnabled && !isWaitingForResponse) {
    updateStatus('🔄 Auto-starting recording...', 'processing');
    setTimeout(() => {
      startRecording();
    }, 500);
  }
}

// Helper function to play multiple audio chunks sequentially
async function playAudioSequentially(audioUrls) {
  for (let i = 0; i < audioUrls.length; i++) {
    console.log(`Playing audio chunk ${i + 1}/${audioUrls.length}`);
    
    const audio = new Audio(audioUrls[i]);
    
    // Wait for current chunk to finish before playing next
    await new Promise((resolve) => {
      audio.onended = resolve;
      audio.onerror = () => {
        console.error(`Failed to play chunk ${i + 1}`);
        resolve(); // Continue to next chunk even if one fails
      };
      audio.play().catch(err => {
        console.error(`Error playing chunk ${i + 1}:`, err);
        resolve();
      });
    });
    
    // Small pause between chunks
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  
  console.log("Finished playing all audio chunks");
}

function updateStatus(message, type = 'processing') {
  const statusElement = document.getElementById('conversation-status');
  statusElement.textContent = message;
  statusElement.className = `status ${type}`;
}

// ==================== LEGACY EVENT LISTENERS (Day 9) ====================

function setupLegacyEventListeners() {
  // Legacy text-to-speech
  const submitBtn = document.getElementById("submit-btn");
  const textInput = document.getElementById("text-input");
  const audioPlayer = document.getElementById("audio-player");

  if (submitBtn && textInput && audioPlayer) {
    submitBtn.addEventListener("click", async () => {
      const text = textInput.value.trim();
      if (!text) return alert("Please enter some text!");

      try {
        const res = await fetch("http://127.0.0.1:8000/generate-audio/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ text }),
        });

        const data = await res.json();
        audioPlayer.src = data.audio_url;
        audioPlayer.play();
      } catch (err) {
        console.error("Error:", err);
        alert("Something went wrong while generating audio.");
      }
    });
  }

  // Legacy echo bot functionality
  setupLegacyEchoBot();
}

// ==================== LEGACY ECHO BOT LOGIC ====================

let legacyMediaRecorder;
let legacyAudioChunks = [];
let legacyRecordedBlob;

function setupLegacyEchoBot() {
  const startBtnLegacy = document.getElementById("start-recording-legacy");
  const stopBtnLegacy = document.getElementById("stop-recording-legacy");
  const uploadBtn = document.getElementById("upload-audio");
  const audioPlayerLegacy = document.getElementById("recorded-audio-legacy");
  const statusMsg = document.getElementById("upload-status");

  startBtnLegacy?.addEventListener("click", async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    legacyMediaRecorder = new MediaRecorder(stream);
    legacyAudioChunks = [];

    legacyMediaRecorder.ondataavailable = (event) => {
      legacyAudioChunks.push(event.data);
    };

    legacyMediaRecorder.onstop = () => {
      legacyRecordedBlob = new Blob(legacyAudioChunks, { type: "audio/webm" });
      const audioUrl = URL.createObjectURL(legacyRecordedBlob);
      audioPlayerLegacy.src = audioUrl;
      audioPlayerLegacy.play();
    };

    legacyMediaRecorder.start();
    startBtnLegacy.disabled = true;
    stopBtnLegacy.disabled = false;
  });

  stopBtnLegacy?.addEventListener("click", () => {
    if (legacyMediaRecorder && legacyMediaRecorder.state !== "inactive") {
      legacyMediaRecorder.stop();
      startBtnLegacy.disabled = false;
      stopBtnLegacy.disabled = true;
      document.getElementById("echo-murf").disabled = false;
      document.getElementById("llm-chat").disabled = false;
    }
  });

  uploadBtn?.addEventListener("click", async () => {
    if (!legacyRecordedBlob) return alert("Please record something first!");

    const formData = new FormData();
    formData.append("file", legacyRecordedBlob, "recording.webm");

    statusMsg.textContent = "Uploading...";

    try {
      const res = await fetch("http://127.0.0.1:8000/upload-audio/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      statusMsg.textContent = `✅ Uploaded: ${data.filename} (${data.content_type}), ${data.size} bytes`;
      transcribeAudio(legacyRecordedBlob);
    } catch (err) {
      console.error(err);
      statusMsg.textContent = "❌ Upload failed!";
    }
  });

  // Echo and LLM buttons
  document.getElementById("echo-murf")?.addEventListener("click", handleEchoMurf);
  document.getElementById("llm-chat")?.addEventListener("click", handleLegacyLLMChat);
}

async function transcribeAudio(blob) {
  const formData = new FormData();
  formData.append("file", blob, "recording.wav");

  const statusDiv = document.getElementById("status");
  const transcriptDiv = document.getElementById("transcript");

  statusDiv.innerText = "Transcribing...";

  try {
    const response = await fetch("http://localhost:8000/transcribe/file", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Transcription failed.");
    }

    const data = await response.json();
    statusDiv.innerText = "Transcription complete!";
    transcriptDiv.innerText = data.transcript;
  } catch (err) {
    console.error(err);
    statusDiv.innerText = "Transcription error.";
    transcriptDiv.innerText = "";
  }
}

async function handleEchoMurf() {
  if (!legacyRecordedBlob) {
    alert("Please record something first!");
    return;
  }

  const formData = new FormData();
  formData.append("audio_file", legacyRecordedBlob, "recording.webm");
  
  const voiceSelect = document.getElementById("voiceSelect2");
  if (voiceSelect) {
    formData.append("voiceId", voiceSelect.value);
  }

  const statusMsg = document.getElementById("upload-status");
  statusMsg.textContent = "Processing with Murf...";

  try {
    const res = await fetch("http://127.0.0.1:8000/tts/echo", {
      method: "POST",
      body: formData
    });

    const result = await res.json();

    if (result.error) {
      console.error(result.error);
      alert(result.error);
      statusMsg.textContent = "❌ Echo failed!";
      return;
    }

    console.log("Echo transcription:", result.text);
    statusMsg.textContent = `✅ Echo: "${result.text}"`;
    
    const audioPlayerLegacy = document.getElementById("recorded-audio-legacy");
    audioPlayerLegacy.src = result.audio_url;
    audioPlayerLegacy.play();

  } catch (err) {
    console.error("Error:", err);
    alert("Echo processing failed.");
    statusMsg.textContent = "❌ Echo failed!";
  }
}

async function handleLegacyLLMChat() {
  if (!legacyRecordedBlob) {
    alert("Please record something first!");
    return;
  }

  const formData = new FormData();
  formData.append("audio_file", legacyRecordedBlob, "recording.webm");
  
  const voiceSelect = document.getElementById("voiceSelect2");
  if (voiceSelect) {
    formData.append("voiceId", voiceSelect.value);
  }

  const statusMsg = document.getElementById("upload-status");
  statusMsg.textContent = "🤖 Processing with LLM...";
  
  const transcriptDiv = document.getElementById("transcript");
  const statusDiv = document.getElementById("status");
  
  statusDiv.textContent = "🎯 Transcribing → LLM → TTS...";

  try {
    const res = await fetch("http://127.0.0.1:8000/llm/query", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }

    const result = await res.json();

    if (result.error) {
      console.error(result.error);
      alert(result.error);
      statusMsg.textContent = "❌ LLM processing failed!";
      return;
    }

    console.log("User input:", result.input);
    console.log("LLM response:", result.response);
    console.log("Audio chunks:", result.chunks_count);
    
    transcriptDiv.innerHTML = `
      <strong>You said:</strong> "${result.input}"<br>
      <strong>LLM response:</strong> "${result.response}"<br>
      <strong>Voice:</strong> ${result.voice_id}
    `;
    
    statusDiv.textContent = result.chunks_count > 1 
      ? `✅ LLM Chat complete! (${result.chunks_count} audio chunks)`
      : "✅ LLM Chat complete!";
    
    statusMsg.textContent = `🤖 LLM: "${result.input}" → Response generated!`;
    
    const audioPlayerLegacy = document.getElementById("recorded-audio-legacy");
    if (result.audio_url) {
      audioPlayerLegacy.src = result.audio_url;
      audioPlayerLegacy.play();
      
      if (result.audio_urls && result.audio_urls.length > 1) {
        playAudioSequentially(result.audio_urls);
      }
    }

  } catch (err) {
    console.error("Error:", err);
    alert(`LLM processing failed: ${err.message}`);
    statusMsg.textContent = "❌ LLM failed!";
    statusDiv.textContent = "LLM processing error.";
  }
}