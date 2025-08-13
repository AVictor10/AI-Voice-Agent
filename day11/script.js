// // Global variables
// let mediaRecorder;
// let audioChunks = [];
// let recordedBlob;
// let currentSessionId = '';
// let autoRecordEnabled = false;
// let isWaitingForResponse = false;

// // Initialize session management when page loads
// document.addEventListener("DOMContentLoaded", () => {
//   initializeSession();
//   setupEventListeners();
//   setupLegacyEventListeners();
// });

// // ==================== SESSION MANAGEMENT ====================

// function initializeSession() {
//   // Get session ID from URL params or generate new one
//   const urlParams = new URLSearchParams(window.location.search);
//   const sessionFromUrl = urlParams.get('session');
  
//   if (sessionFromUrl) {
//     currentSessionId = sessionFromUrl;
//   } else {
//     currentSessionId = generateSessionId();
//     // Update URL with session ID
//     const newUrl = `${window.location.pathname}?session=${currentSessionId}`;
//     window.history.replaceState({}, '', newUrl);
//   }
  
//   document.getElementById('current-session').textContent = currentSessionId;
//   loadSessionHistory();
// }

// function generateSessionId() {
//   return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
// }

// function updateSessionInUrl(sessionId) {
//   const newUrl = `${window.location.pathname}?session=${sessionId}`;
//   window.history.pushState({}, '', newUrl);
// }

// async function loadSessionHistory() {
//   try {
//     const response = await fetch(`http://127.0.0.1:8000/agent/history/${currentSessionId}`);
//     const data = await response.json();
    
//     if (data.status === 'success') {
//       updateSessionInfo(data.conversation_turns, data.message_count);
//       displayChatHistory(data.history);
//     }
//   } catch (error) {
//     console.error('Failed to load session history:', error);
//   }
// }

// function updateSessionInfo(turns, messages) {
//   document.getElementById('conversation-turns').textContent = turns;
//   document.getElementById('total-messages').textContent = messages;
// }

// function displayChatHistory(history) {
//   const historyContainer = document.getElementById('history-messages');
//   historyContainer.innerHTML = '';
  
//   history.forEach(message => {
//     const messageDiv = document.createElement('div');
//     messageDiv.className = `chat-message ${message.role}`;
    
//     const time = new Date(message.timestamp * 1000).toLocaleTimeString();
//     messageDiv.innerHTML = `
//       <div class="message-content">${message.content}</div>
//       <div class="message-time">${time}</div>
//     `;
    
//     historyContainer.appendChild(messageDiv);
//   });
  
//   // Scroll to bottom
//   historyContainer.scrollTop = historyContainer.scrollHeight;
// }

// // ==================== EVENT LISTENERS SETUP ====================

// function setupEventListeners() {
//   // Session management
//   document.getElementById('new-session-btn').addEventListener('click', createNewSession);
//   document.getElementById('clear-history-btn').addEventListener('click', clearCurrentSession);
//   document.getElementById('load-session-btn').addEventListener('click', loadCustomSession);
  
//   // Recording controls
//   document.getElementById('start-recording').addEventListener('click', startRecording);
//   document.getElementById('stop-recording').addEventListener('click', stopRecording);
//   document.getElementById('chat-conversation').addEventListener('click', sendToAI);
  
//   // Auto-record toggle (click on indicator)
//   document.getElementById('auto-record-status').addEventListener('click', toggleAutoRecord);
// }

// // ==================== SESSION CONTROL FUNCTIONS ====================

// function createNewSession() {
//   currentSessionId = generateSessionId();
//   document.getElementById('current-session').textContent = currentSessionId;
//   updateSessionInUrl(currentSessionId);
//   updateSessionInfo(0, 0);
//   document.getElementById('history-messages').innerHTML = '';
//   updateStatus('🆕 New session created!', 'success');
// }

// async function clearCurrentSession() {
//   try {
//     const response = await fetch(`http://127.0.0.1:8000/agent/history/${currentSessionId}`, {
//       method: 'DELETE'
//     });
    
//     if (response.ok) {
//       updateSessionInfo(0, 0);
//       document.getElementById('history-messages').innerHTML = '';
//       updateStatus('🗑️ Session history cleared!', 'success');
//     }
//   } catch (error) {
//     console.error('Failed to clear session:', error);
//     updateStatus('❌ Failed to clear session', 'error');
//   }
// }

// function loadCustomSession() {
//   const customSessionInput = document.getElementById('custom-session-input');
//   const sessionId = customSessionInput.value.trim();
  
//   if (!sessionId) {
//     alert('Please enter a session ID');
//     return;
//   }
  
//   currentSessionId = sessionId;
//   document.getElementById('current-session').textContent = currentSessionId;
//   updateSessionInUrl(currentSessionId);
//   customSessionInput.value = '';
//   loadSessionHistory();
//   updateStatus('📂 Session loaded!', 'success');
// }

// function toggleAutoRecord() {
//   autoRecordEnabled = !autoRecordEnabled;
//   const indicator = document.getElementById('auto-record-status');
//   indicator.textContent = `Auto-record: ${autoRecordEnabled ? 'ON' : 'OFF'}`;
//   indicator.style.background = autoRecordEnabled 
//     ? 'linear-gradient(135deg, #20bf6b 0%, #26d0ce 100%)'
//     : 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)';
// }

// // ==================== RECORDING FUNCTIONS ====================

// async function startRecording() {
//   try {
//     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
//     mediaRecorder = new MediaRecorder(stream);
//     audioChunks = [];

//     mediaRecorder.ondataavailable = (event) => {
//       audioChunks.push(event.data);
//     };

//     mediaRecorder.onstop = () => {
//       recordedBlob = new Blob(audioChunks, { type: "audio/webm" });
//       const audioUrl = URL.createObjectURL(recordedBlob);
//       document.getElementById('recorded-audio').src = audioUrl;
      
//       // Enable send button
//       document.getElementById('chat-conversation').disabled = false;
      
//       updateStatus('🎤 Recording complete! Ready to send to AI.', 'success');
//     };

//     mediaRecorder.start();
    
//     // Update UI
//     document.getElementById('start-recording').disabled = true;
//     document.getElementById('start-recording').classList.add('recording');
//     document.getElementById('stop-recording').disabled = false;
    
//     updateStatus('🔴 Recording...', 'processing');
    
//   } catch (error) {
//     console.error('Error starting recording:', error);
//     updateStatus('❌ Failed to start recording', 'error');
//   }
// }

// function stopRecording() {
//   if (mediaRecorder && mediaRecorder.state !== "inactive") {
//     mediaRecorder.stop();
    
//     // Update UI
//     document.getElementById('start-recording').disabled = false;
//     document.getElementById('start-recording').classList.remove('recording');
//     document.getElementById('stop-recording').disabled = true;
    
//     // Stop all tracks to free up microphone
//     mediaRecorder.stream.getTracks().forEach(track => track.stop());
//   }
// }

// // ==================== AI CONVERSATION FUNCTIONS ====================

// async function sendToAI() {
//   if (!recordedBlob) {
//     alert("Please record something first!");
//     return;
//   }

//   const formData = new FormData();
//   formData.append("audio_file", recordedBlob, "recording.webm");
  
//   // Add voice selection
//   const voiceSelect = document.getElementById("voiceSelect");
//   if (voiceSelect) {
//     formData.append("voiceId", voiceSelect.value);
//   }

//   updateStatus('🤖 Processing with AI...', 'processing');
//   isWaitingForResponse = true;
  
//   // Disable send button while processing
//   document.getElementById('chat-conversation').disabled = true;

//   try {
//     const response = await fetch(`http://127.0.0.1:8000/agent/chat/${currentSessionId}`, {
//       method: "POST",
//       body: formData
//     });

//     if (!response.ok) {
//       throw new Error(`HTTP ${response.status}: ${response.statusText}`);
//     }

//     const result = await response.json();

//     if (result.error) {
//       throw new Error(result.error);
//     }

//     // Update session info
//     updateSessionInfo(result.conversation_turns, result.conversation_length);

//     // Display the conversation
//     updateStatus(`✅ AI Response: "${result.response.substring(0, 100)}..."`, 'success');

//     // Play the AI response audio
//     if (result.audio_url) {
//       const aiAudio = document.getElementById('ai-response-audio');
//       aiAudio.src = result.audio_url;
      
//       // Play the response
//       await aiAudio.play();
      
//       // If multiple chunks, play them sequentially
//       if (result.audio_urls && result.audio_urls.length > 1) {
//         await playAudioSequentially(result.audio_urls);
//       }
      
//       // Set up auto-record after audio finishes
//       if (autoRecordEnabled) {
//         aiAudio.onended = () => {
//           setTimeout(() => {
//             if (!isWaitingForResponse) return; // Safety check
//             startAutoRecord();
//           }, 1000); // 1 second delay after AI response ends
//         };
//       }
//     }

//     // Refresh chat history
//     loadSessionHistory();
    
//     isWaitingForResponse = false;

//   } catch (error) {
//     console.error("Error:", error);
//     updateStatus(`❌ AI processing failed: ${error.message}`, 'error');
//     isWaitingForResponse = false;
//   }
// }

// async function startAutoRecord() {
//   if (autoRecordEnabled && !isWaitingForResponse) {
//     updateStatus('🔄 Auto-starting recording...', 'processing');
//     setTimeout(() => {
//       startRecording();
//     }, 500);
//   }
// }

// // Helper function to play multiple audio chunks sequentially
// async function playAudioSequentially(audioUrls) {
//   for (let i = 0; i < audioUrls.length; i++) {
//     console.log(`Playing audio chunk ${i + 1}/${audioUrls.length}`);
    
//     const audio = new Audio(audioUrls[i]);
    
//     // Wait for current chunk to finish before playing next
//     await new Promise((resolve) => {
//       audio.onended = resolve;
//       audio.onerror = () => {
//         console.error(`Failed to play chunk ${i + 1}`);
//         resolve(); // Continue to next chunk even if one fails
//       };
//       audio.play().catch(err => {
//         console.error(`Error playing chunk ${i + 1}:`, err);
//         resolve();
//       });
//     });
    
//     // Small pause between chunks
//     await new Promise(resolve => setTimeout(resolve, 200));
//   }
  
//   console.log("Finished playing all audio chunks");
// }

// function updateStatus(message, type = 'processing') {
//   const statusElement = document.getElementById('conversation-status');
//   statusElement.textContent = message;
//   statusElement.className = `status ${type}`;
// }

// // ==================== LEGACY EVENT LISTENERS (Day 9) ====================

// function setupLegacyEventListeners() {
//   // Legacy text-to-speech
//   const submitBtn = document.getElementById("submit-btn");
//   const textInput = document.getElementById("text-input");
//   const audioPlayer = document.getElementById("audio-player");

//   if (submitBtn && textInput && audioPlayer) {
//     submitBtn.addEventListener("click", async () => {
//       const text = textInput.value.trim();
//       if (!text) return alert("Please enter some text!");

//       try {
//         const res = await fetch("http://127.0.0.1:8000/generate-audio/", {
//           method: "POST",
//           headers: {
//             "Content-Type": "application/json",
//           },
//           body: JSON.stringify({ text }),
//         });

//         const data = await res.json();
//         audioPlayer.src = data.audio_url;
//         audioPlayer.play();
//       } catch (err) {
//         console.error("Error:", err);
//         alert("Something went wrong while generating audio.");
//       }
//     });
//   }

//   // Legacy echo bot functionality
//   setupLegacyEchoBot();
// }

// // ==================== LEGACY ECHO BOT LOGIC ====================

// let legacyMediaRecorder;
// let legacyAudioChunks = [];
// let legacyRecordedBlob;

// function setupLegacyEchoBot() {
//   const startBtnLegacy = document.getElementById("start-recording-legacy");
//   const stopBtnLegacy = document.getElementById("stop-recording-legacy");
//   const uploadBtn = document.getElementById("upload-audio");
//   const audioPlayerLegacy = document.getElementById("recorded-audio-legacy");
//   const statusMsg = document.getElementById("upload-status");

//   startBtnLegacy?.addEventListener("click", async () => {
//     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

//     legacyMediaRecorder = new MediaRecorder(stream);
//     legacyAudioChunks = [];

//     legacyMediaRecorder.ondataavailable = (event) => {
//       legacyAudioChunks.push(event.data);
//     };

//     legacyMediaRecorder.onstop = () => {
//       legacyRecordedBlob = new Blob(legacyAudioChunks, { type: "audio/webm" });
//       const audioUrl = URL.createObjectURL(legacyRecordedBlob);
//       audioPlayerLegacy.src = audioUrl;
//       audioPlayerLegacy.play();
//     };

//     legacyMediaRecorder.start();
//     startBtnLegacy.disabled = true;
//     stopBtnLegacy.disabled = false;
//   });

//   stopBtnLegacy?.addEventListener("click", () => {
//     if (legacyMediaRecorder && legacyMediaRecorder.state !== "inactive") {
//       legacyMediaRecorder.stop();
//       startBtnLegacy.disabled = false;
//       stopBtnLegacy.disabled = true;
//       document.getElementById("echo-murf").disabled = false;
//       document.getElementById("llm-chat").disabled = false;
//     }
//   });

//   uploadBtn?.addEventListener("click", async () => {
//     if (!legacyRecordedBlob) return alert("Please record something first!");

//     const formData = new FormData();
//     formData.append("file", legacyRecordedBlob, "recording.webm");

//     statusMsg.textContent = "Uploading...";

//     try {
//       const res = await fetch("http://127.0.0.1:8000/upload-audio/", {
//         method: "POST",
//         body: formData,
//       });

//       const data = await res.json();
//       statusMsg.textContent = `✅ Uploaded: ${data.filename} (${data.content_type}), ${data.size} bytes`;
//       transcribeAudio(legacyRecordedBlob);
//     } catch (err) {
//       console.error(err);
//       statusMsg.textContent = "❌ Upload failed!";
//     }
//   });

//   // Echo and LLM buttons
//   document.getElementById("echo-murf")?.addEventListener("click", handleEchoMurf);
//   document.getElementById("llm-chat")?.addEventListener("click", handleLegacyLLMChat);
// }

// async function transcribeAudio(blob) {
//   const formData = new FormData();
//   formData.append("file", blob, "recording.wav");

//   const statusDiv = document.getElementById("status");
//   const transcriptDiv = document.getElementById("transcript");

//   statusDiv.innerText = "Transcribing...";

//   try {
//     const response = await fetch("http://localhost:8000/transcribe/file", {
//       method: "POST",
//       body: formData,
//     });

//     if (!response.ok) {
//       throw new Error("Transcription failed.");
//     }

//     const data = await response.json();
//     statusDiv.innerText = "Transcription complete!";
//     transcriptDiv.innerText = data.transcript;
//   } catch (err) {
//     console.error(err);
//     statusDiv.innerText = "Transcription error.";
//     transcriptDiv.innerText = "";
//   }
// }

// async function handleEchoMurf() {
//   if (!legacyRecordedBlob) {
//     alert("Please record something first!");
//     return;
//   }

//   const formData = new FormData();
//   formData.append("audio_file", legacyRecordedBlob, "recording.webm");
  
//   const voiceSelect = document.getElementById("voiceSelect2");
//   if (voiceSelect) {
//     formData.append("voiceId", voiceSelect.value);
//   }

//   const statusMsg = document.getElementById("upload-status");
//   statusMsg.textContent = "Processing with Murf...";

//   try {
//     const res = await fetch("http://127.0.0.1:8000/tts/echo", {
//       method: "POST",
//       body: formData
//     });

//     const result = await res.json();

//     if (result.error) {
//       console.error(result.error);
//       alert(result.error);
//       statusMsg.textContent = "❌ Echo failed!";
//       return;
//     }

//     console.log("Echo transcription:", result.text);
//     statusMsg.textContent = `✅ Echo: "${result.text}"`;
    
//     const audioPlayerLegacy = document.getElementById("recorded-audio-legacy");
//     audioPlayerLegacy.src = result.audio_url;
//     audioPlayerLegacy.play();

//   } catch (err) {
//     console.error("Error:", err);
//     alert("Echo processing failed.");
//     statusMsg.textContent = "❌ Echo failed!";
//   }
// }

// async function handleLegacyLLMChat() {
//   if (!legacyRecordedBlob) {
//     alert("Please record something first!");
//     return;
//   }

//   const formData = new FormData();
//   formData.append("audio_file", legacyRecordedBlob, "recording.webm");
  
//   const voiceSelect = document.getElementById("voiceSelect2");
//   if (voiceSelect) {
//     formData.append("voiceId", voiceSelect.value);
//   }

//   const statusMsg = document.getElementById("upload-status");
//   statusMsg.textContent = "🤖 Processing with LLM...";
  
//   const transcriptDiv = document.getElementById("transcript");
//   const statusDiv = document.getElementById("status");
  
//   statusDiv.textContent = "🎯 Transcribing → LLM → TTS...";

//   try {
//     const res = await fetch("http://127.0.0.1:8000/llm/query", {
//       method: "POST",
//       body: formData
//     });

//     if (!res.ok) {
//       throw new Error(`HTTP ${res.status}: ${res.statusText}`);
//     }

//     const result = await res.json();

//     if (result.error) {
//       console.error(result.error);
//       alert(result.error);
//       statusMsg.textContent = "❌ LLM processing failed!";
//       return;
//     }

//     console.log("User input:", result.input);
//     console.log("LLM response:", result.response);
//     console.log("Audio chunks:", result.chunks_count);
    
//     transcriptDiv.innerHTML = `
//       <strong>You said:</strong> "${result.input}"<br>
//       <strong>LLM response:</strong> "${result.response}"<br>
//       <strong>Voice:</strong> ${result.voice_id}
//     `;
    
//     statusDiv.textContent = result.chunks_count > 1 
//       ? `✅ LLM Chat complete! (${result.chunks_count} audio chunks)`
//       : "✅ LLM Chat complete!";
    
//     statusMsg.textContent = `🤖 LLM: "${result.input}" → Response generated!`;
    
//     const audioPlayerLegacy = document.getElementById("recorded-audio-legacy");
//     if (result.audio_url) {
//       audioPlayerLegacy.src = result.audio_url;
//       audioPlayerLegacy.play();
      
//       if (result.audio_urls && result.audio_urls.length > 1) {
//         playAudioSequentially(result.audio_urls);
//       }
//     }

//   } catch (err) {
//     console.error("Error:", err);
//     alert(`LLM processing failed: ${err.message}`);
//     statusMsg.textContent = "❌ LLM failed!";
//     statusDiv.textContent = "LLM processing error.";
//   }
// }



// Global variables
let mediaRecorder;
let audioChunks = [];
let recordedBlob;
let currentSessionId = '';
let autoRecordEnabled = false;
let isWaitingForResponse = false;
let retryCount = 0;
const MAX_RETRIES = 3;

// Error handling configuration
const ERROR_CONFIG = {
  showNotifications: true,
  playErrorSounds: true,
  autoRetry: true,
  fallbackAudioEnabled: true
};

// Fallback error audio URLs - you should host these or generate them
const FALLBACK_AUDIO_URLS = {
  stt_failure: "/static/audio/stt_error.mp3",
  llm_failure: "/static/audio/llm_error.mp3", 
  tts_failure: "/static/audio/tts_error.mp3",
  general_failure: "/static/audio/general_error.mp3",
  network_error: "/static/audio/network_error.mp3"
};

// Initialize session management when page loads
document.addEventListener("DOMContentLoaded", () => {
  initializeSession();
  setupEventListeners();
  setupLegacyEventListeners();
  setupErrorHandling();
  checkServerHealth();
});

// ==================== ERROR HANDLING SETUP ====================

function setupErrorHandling() {
  // Set up global error handlers
  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showError('An unexpected error occurred', 'general_failure');
  });

  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showError('An unexpected error occurred', 'general_failure');
    event.preventDefault();
  });

  // Set up network status monitoring
  window.addEventListener('online', () => {
    updateStatus('🟢 Connection restored', 'success');
    hideError();
  });

  window.addEventListener('offline', () => {
    showError('No internet connection. Please check your network.', 'network_error');
    updateStatus('🔴 No internet connection', 'error');
  });
}

async function checkServerHealth() {
  try {
    const response = await fetch('http://127.0.0.1:8000/health', {
      method: 'GET',
      signal: AbortSignal.timeout(5000)
    });
    
    if (!response.ok) {
      throw new Error(`Server health check failed: ${response.status}`);
    }
    
    const health = await response.json();
    displayHealthStatus(health);
    
    if (health.status === 'degraded') {
      showWarning('Some services are currently unavailable. Functionality may be limited.');
    }
    
  } catch (error) {
    console.error('Server health check failed:', error);
    showError('Cannot connect to the server. Please make sure it is running.', 'network_error');
  }
}

function displayHealthStatus(health) {
  const statusElement = document.getElementById('server-status');
  if (statusElement) {
    const statusColor = health.status === 'healthy' ? '#28a745' : 
                       health.status === 'degraded' ? '#ffc107' : '#dc3545';
    
    statusElement.innerHTML = `
      <div style="color: ${statusColor};">
        Server: ${health.status.toUpperCase()}
        <br>STT: ${health.apis.assemblyai.status}
        <br>LLM: ${health.apis.gemini.status} 
        <br>TTS: ${health.apis.murf.status}
      </div>
    `;
  }
}

// ==================== ERROR DISPLAY FUNCTIONS ====================

function showError(message, errorType = 'general_failure', showRetry = false) {
  console.error(`[${errorType}] ${message}`);
  
  // Update status display
  updateStatus(`❌ ${message}`, 'error');
  
  // Show error notification
  if (ERROR_CONFIG.showNotifications) {
    showNotification(message, 'error', showRetry);
  }
  
  // Play error audio if available and enabled
  if (ERROR_CONFIG.playErrorSounds && ERROR_CONFIG.fallbackAudioEnabled) {
    playFallbackAudio(errorType);
  }
  
  // Show error in dedicated error container
  const errorContainer = document.getElementById('error-container');
  if (errorContainer) {
    errorContainer.innerHTML = `
      <div class="error-message ${errorType}">
        <span class="error-icon">⚠️</span>
        <span class="error-text">${message}</span>
        ${showRetry ? '<button onclick="retryLastAction()" class="retry-btn">🔄 Retry</button>' : ''}
        <button onclick="hideError()" class="close-btn">✖️</button>
      </div>
    `;
    errorContainer.style.display = 'block';
  }
}

function showWarning(message) {
  updateStatus(`⚠️ ${message}`, 'warning');
  
  const warningContainer = document.getElementById('warning-container');
  if (warningContainer) {
    warningContainer.innerHTML = `
      <div class="warning-message">
        <span class="warning-icon">⚠️</span>
        <span class="warning-text">${message}</span>
        <button onclick="hideWarning()" class="close-btn">✖️</button>
      </div>
    `;
    warningContainer.style.display = 'block';
  }
}

function hideError() {
  const errorContainer = document.getElementById('error-container');
  if (errorContainer) {
    errorContainer.style.display = 'none';
  }
}

function hideWarning() {
  const warningContainer = document.getElementById('warning-container');
  if (warningContainer) {
    warningContainer.style.display = 'none';
  }
}

function showNotification(message, type = 'info', showRetry = false) {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.innerHTML = `
    <div class="notification-content">
      <span>${message}</span>
      ${showRetry ? '<button onclick="retryLastAction()" class="notification-retry">Retry</button>' : ''}
    </div>
  `;
  
  // Add to page
  document.body.appendChild(notification);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 5000);
}

async function playFallbackAudio(errorType) {
  try {
    const audioUrl = FALLBACK_AUDIO_URLS[errorType];
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.volume = 0.7;
      await audio.play();
    }
  } catch (error) {
    console.warn('Could not play fallback audio:', error);
  }
}

// ==================== RETRY LOGIC ====================

let lastAction = null;

function setLastAction(action, params) {
  lastAction = { action, params };
}

async function retryLastAction() {
  if (!lastAction) {
    showError('No action to retry');
    return;
  }
  
  retryCount++;
  
  if (retryCount > MAX_RETRIES) {
    showError('Maximum retry attempts reached. Please try again later.', 'general_failure');
    retryCount = 0;
    return;
  }
  
  updateStatus(`🔄 Retrying... (${retryCount}/${MAX_RETRIES})`, 'processing');
  
  try {
    switch (lastAction.action) {
      case 'sendToAI':
        await sendToAI();
        break;
      case 'startRecording':
        await startRecording();
        break;
      case 'transcribeAndProcess':
        await transcribeAndProcess(lastAction.params.audioBlob, lastAction.params.voiceId);
        break;
      default:
        showError('Unknown action to retry');
    }
  } catch (error) {
    console.error('Retry failed:', error);
    showError(`Retry failed: ${error.message}`, 'general_failure', retryCount < MAX_RETRIES);
  }
}

// ==================== ENHANCED API COMMUNICATION ====================

async function makeRobustAPICall(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options.timeout || 30000);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
    
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      throw new Error('Request timeout - the server is taking too long to respond');
    }
    
    if (!navigator.onLine) {
      throw new Error('No internet connection');
    }
    
    throw error;
  }
}

// ==================== SESSION MANAGEMENT ====================

function initializeSession() {
  const urlParams = new URLSearchParams(window.location.search);
  const sessionFromUrl = urlParams.get('session');
  
  if (sessionFromUrl) {
    currentSessionId = sessionFromUrl;
  } else {
    currentSessionId = generateSessionId();
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
    const data = await makeRobustAPICall(`http://127.0.0.1:8000/agent/history/${currentSessionId}`);
    
    if (data.status === 'success') {
      updateSessionInfo(data.conversation_turns, data.message_count);
      displayChatHistory(data.history);
    } else if (data.error) {
      console.warn('Failed to load session history:', data.error_message);
    }
  } catch (error) {
    console.error('Failed to load session history:', error);
    showWarning('Could not load conversation history');
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
  
  historyContainer.scrollTop = historyContainer.scrollHeight;
}

// ==================== EVENT LISTENERS SETUP ====================

function setupEventListeners() {
  document.getElementById('new-session-btn').addEventListener('click', createNewSession);
  document.getElementById('clear-history-btn').addEventListener('click', clearCurrentSession);
  document.getElementById('load-session-btn').addEventListener('click', loadCustomSession);
  
  document.getElementById('start-recording').addEventListener('click', startRecording);
  document.getElementById('stop-recording').addEventListener('click', stopRecording);
  document.getElementById('chat-conversation').addEventListener('click', sendToAI);
  
  document.getElementById('auto-record-status').addEventListener('click', toggleAutoRecord);
  
  // Add error simulation buttons for testing
  document.getElementById('simulate-stt-error')?.addEventListener('click', () => simulateError('stt'));
  document.getElementById('simulate-llm-error')?.addEventListener('click', () => simulateError('llm'));
  document.getElementById('simulate-tts-error')?.addEventListener('click', () => simulateError('tts'));
  document.getElementById('reset-errors')?.addEventListener('click', () => simulateError('reset'));
}

function setupLegacyEventListeners() {
  // Set up legacy event listeners for backward compatibility
  const legacyButtons = document.querySelectorAll('[data-legacy-action]');
  legacyButtons.forEach(button => {
    const action = button.getAttribute('data-legacy-action');
    button.addEventListener('click', () => {
      console.log(`Legacy action triggered: ${action}`);
      // Handle legacy actions here if needed
    });
  });
}

// ==================== ERROR SIMULATION FOR TESTING ====================

async function simulateError(errorType) {
  try {
    const response = await makeRobustAPICall(`http://127.0.0.1:8000/simulate-error/${errorType}`, {
      method: 'POST'
    });
    
    updateStatus(`🔧 ${response.message}`, errorType === 'reset' ? 'success' : 'warning');
    
    if (errorType === 'reset') {
      checkServerHealth();
    }
    
  } catch (error) {
    showError(`Failed to simulate error: ${error.message}`, 'general_failure');
  }
}

// ==================== SESSION CONTROL FUNCTIONS ====================

function createNewSession() {
  currentSessionId = generateSessionId();
  document.getElementById('current-session').textContent = currentSessionId;
  updateSessionInUrl(currentSessionId);
  updateSessionInfo(0, 0);
  document.getElementById('history-messages').innerHTML = '';
  updateStatus('🆕 New session created!', 'success');
  retryCount = 0; // Reset retry count for new session
}

async function clearCurrentSession() {
  try {
    const response = await makeRobustAPICall(`http://127.0.0.1:8000/agent/history/${currentSessionId}`, {
      method: 'DELETE'
    });
    
    if (response.error) {
      showError(response.error_message, 'general_failure');
      return;
    }
    
    updateSessionInfo(0, 0);
    document.getElementById('history-messages').innerHTML = '';
    updateStatus('🗑️ Session history cleared!', 'success');
    
  } catch (error) {
    console.error('Failed to clear session:', error);
    showError('Failed to clear session history', 'general_failure', true);
    setLastAction('clearCurrentSession', {});
  }
}

function loadCustomSession() {
  const customSessionInput = document.getElementById('custom-session-input');
  const sessionId = customSessionInput.value.trim();
  
  if (!sessionId) {
    showError('Please enter a session ID');
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
    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
    : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
  
  updateStatus(`🔄 Auto-record ${autoRecordEnabled ? 'enabled' : 'disabled'}`, 'info');
}

// ==================== RECORDING FUNCTIONS ====================

async function startRecording() {
  try {
    if (isWaitingForResponse) {
      showWarning('Please wait for the current response to complete');
      return;
    }

    setLastAction('startRecording', {});
    
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      } 
    });
    
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    });
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };
    
    mediaRecorder.onstop = async () => {
      try {
        recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        if (recordedBlob.size === 0) {
          showError('No audio was recorded. Please try again.', 'general_failure', true);
          return;
        }
        
        const voiceId = document.getElementById('voice-select')?.value || 'en-US-natalie';
        await transcribeAndProcess(recordedBlob, voiceId);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
        
      } catch (error) {
        console.error('Error processing recording:', error);
        showError('Failed to process recording', 'general_failure', true);
        setLastAction('transcribeAndProcess', { audioBlob: recordedBlob, voiceId });
      }
    };
    
    mediaRecorder.onerror = (event) => {
      console.error('MediaRecorder error:', event.error);
      showError('Recording failed. Please check your microphone permissions.', 'general_failure', true);
    };
    
    mediaRecorder.start();
    updateRecordingUI(true);
    updateStatus('🎤 Recording...', 'recording');
    
    // Reset retry count on successful start
    retryCount = 0;
    
  } catch (error) {
    console.error('Failed to start recording:', error);
    if (error.name === 'NotAllowedError') {
      showError('Microphone access denied. Please enable microphone permissions and try again.', 'general_failure');
    } else if (error.name === 'NotFoundError') {
      showError('No microphone found. Please connect a microphone and try again.', 'general_failure');
    } else {
      showError('Failed to start recording. Please check your microphone and try again.', 'general_failure', true);
    }
  }
}

function stopRecording() {
  try {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      updateRecordingUI(false);
      updateStatus('⏹️ Processing recording...', 'processing');
    } else {
      showWarning('No active recording to stop');
    }
  } catch (error) {
    console.error('Error stopping recording:', error);
    showError('Failed to stop recording', 'general_failure');
  }
}

function updateRecordingUI(isRecording) {
  const startButton = document.getElementById('start-recording');
  const stopButton = document.getElementById('stop-recording');
  
  if (startButton) {
    startButton.disabled = isRecording;
    startButton.textContent = isRecording ? '🎤 Recording...' : '🎤 Start Recording';
  }
  
  if (stopButton) {
    stopButton.disabled = !isRecording;
    stopButton.textContent = isRecording ? '⏹️ Stop Recording' : '⏹️ Stop (Inactive)';
  }
}

// ==================== TRANSCRIPTION AND PROCESSING ====================

async function transcribeAndProcess(audioBlob, voiceId = 'en-US-natalie') {
  try {
    isWaitingForResponse = true;
    setLastAction('transcribeAndProcess', { audioBlob, voiceId });
    
    updateStatus('🔄 Transcribing and processing...', 'processing');
    
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.webm');
    formData.append('voiceId', voiceId);
    
    const response = await makeRobustAPICall(`http://127.0.0.1:8000/agent/chat/${currentSessionId}`, {
      method: 'POST',
      body: formData,
      timeout: 60000 // 60 second timeout for full processing
    });
    
    await handleAPIResponse(response);
    
  } catch (error) {
    console.error('Error in transcribeAndProcess:', error);
    
    if (error.message.includes('timeout')) {
      showError('The request took too long. Please try with a shorter recording.', 'timeout', true);
    } else if (error.message.includes('No internet')) {
      showError('No internet connection. Please check your network and try again.', 'network_error', true);
    } else {
      showError('Failed to process audio. Please try again.', 'general_failure', true);
    }
  } finally {
    isWaitingForResponse = false;
    updateRecordingUI(false);
  }
}

// ==================== TEXT INPUT PROCESSING ====================

async function sendToAI() {
  try {
    if (isWaitingForResponse) {
      showWarning('Please wait for the current response to complete');
      return;
    }

    const textInput = document.getElementById('text-input');
    const text = textInput?.value?.trim();
    
    if (!text) {
      showError('Please enter some text to send');
      return;
    }
    
    setLastAction('sendToAI', {});
    isWaitingForResponse = true;
    
    updateStatus('🔄 Processing your message...', 'processing');
    
    const voiceId = document.getElementById('voice-select')?.value || 'en-US-natalie';
    
    const formData = new FormData();
    formData.append('text', text);
    formData.append('voiceId', voiceId);
    
    const response = await makeRobustAPICall(`http://127.0.0.1:8000/agent/chat/${currentSessionId}`, {
      method: 'POST',
      body: formData,
      timeout: 60000
    });
    
    await handleAPIResponse(response);
    
    // Clear text input on success
    if (textInput) {
      textInput.value = '';
    }
    
    // Reset retry count on success
    retryCount = 0;
    
  } catch (error) {
    console.error('Error in sendToAI:', error);
    
    if (error.message.includes('timeout')) {
      showError('The request took too long. Please try again.', 'timeout', true);
    } else if (error.message.includes('No internet')) {
      showError('No internet connection. Please check your network and try again.', 'network_error', true);
    } else {
      showError('Failed to process your message. Please try again.', 'general_failure', true);
    }
  } finally {
    isWaitingForResponse = false;
  }
}

// ==================== RESPONSE HANDLING ====================

async function handleAPIResponse(response) {
  try {
    console.log('API Response:', response);
    
    // Handle error responses
    if (response.error) {
      await handleErrorResponse(response);
      return;
    }
    
    // Handle successful responses
    if (response.status === 'success' || response.status === 'success_no_audio') {
      await handleSuccessResponse(response);
    } else {
      showError('Unexpected response format from server', 'general_failure');
    }
    
  } catch (error) {
    console.error('Error handling API response:', error);
    showError('Failed to process server response', 'general_failure');
  }
}

async function handleErrorResponse(response) {
  const errorType = response.error_type || 'general_failure';
  const errorMessage = response.error_message || 'An unexpected error occurred';
  
  // Show error with appropriate retry option
  showError(errorMessage, errorType, retryCount < MAX_RETRIES);
  
  // Play fallback audio if available
  if (response.fallback_audio_url) {
    try {
      const audio = new Audio(response.fallback_audio_url);
      audio.volume = 0.7;
      await audio.play();
    } catch (audioError) {
      console.warn('Could not play fallback audio:', audioError);
    }
  }
  
  // Update chat history if we have some response text
  if (response.response) {
    addMessageToChat('assistant', response.response, true); // Mark as error response
  }
  
  // Update session info if available
  if (response.session_id) {
    loadSessionHistory();
  }
}

async function handleSuccessResponse(response) {
  // Add messages to chat
  if (response.input) {
    addMessageToChat('user', response.input);
  }
  
  if (response.response) {
    addMessageToChat('assistant', response.response, response.status === 'success_no_audio');
  }
  
  // Play audio if available
  if (response.audio_urls && response.audio_urls.length > 0) {
    await playResponseAudio(response.audio_urls);
  } else if (response.audio_url) {
    await playResponseAudio([response.audio_url]);
  } else if (response.tts_error) {
    // Show TTS error but don't fail the entire response
    showWarning(response.tts_error_message || 'Audio generation failed, but here\'s the text response');
  }
  
  // Update session information
  if (response.conversation_turns !== undefined) {
    updateSessionInfo(response.conversation_turns, response.conversation_length);
  }
  
  updateStatus('✅ Response completed!', 'success');
  
  // Auto-record next message if enabled
  if (autoRecordEnabled && !isWaitingForResponse) {
    setTimeout(() => {
      if (!isWaitingForResponse) {
        startRecording();
      }
    }, 1000);
  }
}

async function playResponseAudio(audioUrls) {
  try {
    updateStatus('🔊 Playing audio response...', 'playing');
    
    for (let i = 0; i < audioUrls.length; i++) {
      const audioUrl = audioUrls[i];
      console.log(`Playing audio chunk ${i + 1}/${audioUrls.length}: ${audioUrl}`);
      
      const audio = new Audio(audioUrl);
      audio.volume = 0.8;
      
      // Wait for this audio chunk to finish before playing next
      await new Promise((resolve, reject) => {
        audio.addEventListener('ended', resolve);
        audio.addEventListener('error', reject);
        audio.play().catch(reject);
      });
    }
    
    updateStatus('🔊 Audio playback completed', 'success');
    
  } catch (error) {
    console.error('Audio playback failed:', error);
    showWarning('Audio playback failed, but you can see the text response above');
  }
}

// ==================== CHAT UI FUNCTIONS ====================

function addMessageToChat(role, content, isError = false) {
  const historyContainer = document.getElementById('history-messages');
  if (!historyContainer) return;
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${role} ${isError ? 'error' : ''}`;
  
  const time = new Date().toLocaleTimeString();
  const errorIndicator = isError ? '<span class="error-indicator">⚠️</span>' : '';
  
  messageDiv.innerHTML = `
    <div class="message-content">${errorIndicator}${content}</div>
    <div class="message-time">${time}</div>
  `;
  
  historyContainer.appendChild(messageDiv);
  historyContainer.scrollTop = historyContainer.scrollHeight;
}

function updateStatus(message, type = 'info') {
  const statusElement = document.getElementById('status-display');
  if (statusElement) {
    statusElement.textContent = message;
    statusElement.className = `status ${type}`;
  }
  
  console.log(`[${type.toUpperCase()}] ${message}`);
}

// ==================== KEYBOARD SHORTCUTS ====================

document.addEventListener('keydown', (event) => {
  // Ctrl/Cmd + Enter to send text
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault();
    sendToAI();
  }
  
  // Space bar to start/stop recording (when not typing in text field)
  if (event.code === 'Space' && event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
    event.preventDefault();
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      stopRecording();
    } else {
      startRecording();
    }
  }
  
  // Escape to clear errors
  if (event.key === 'Escape') {
    hideError();
    hideWarning();
  }
});

// ==================== UTILITY FUNCTIONS ====================

function formatTimestamp(timestamp) {
  return new Date(timestamp * 1000).toLocaleString();
}

function sanitizeHTML(str) {
  const temp = document.createElement('div');
  temp.textContent = str;
  return temp.innerHTML;
}

// ==================== INITIALIZATION CHECK ====================

// Check if all required elements exist
function validateRequiredElements() {
  const requiredElements = [
    'current-session',
    'start-recording',
    'stop-recording',
    'chat-conversation',
    'history-messages',
    'status-display'
  ];
  
  const missingElements = requiredElements.filter(id => !document.getElementById(id));
  
  if (missingElements.length > 0) {
    console.error('Missing required elements:', missingElements);
    showError(`Missing required UI elements: ${missingElements.join(', ')}`, 'general_failure');
  }
}

// Call validation after DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(validateRequiredElements, 100);
});

// ==================== ERROR RECOVERY ====================

// Automatic error recovery
setInterval(() => {
  // Check if we're stuck in a waiting state
  if (isWaitingForResponse) {
    const now = Date.now();
    if (!window.lastRequestTime) {
      window.lastRequestTime = now;
    } else if (now - window.lastRequestTime > 120000) { // 2 minutes timeout
      console.warn('Request appears to be stuck, resetting state');
      isWaitingForResponse = false;
      updateRecordingUI(false);
      showError('Request timed out. Please try again.', 'timeout', true);
      window.lastRequestTime = null;
    }
  } else {
    window.lastRequestTime = null;
  }
}, 10000); // Check every 10 seconds

// ==================== PERFORMANCE MONITORING ====================

// Monitor performance and show warnings for slow responses
function startPerformanceMonitoring() {
  window.requestStartTime = Date.now();
}

function endPerformanceMonitoring() {
  if (window.requestStartTime) {
    const duration = Date.now() - window.requestStartTime;
    console.log(`Request completed in ${duration}ms`);
    
    if (duration > 30000) { // 30 seconds
      showWarning('That took longer than usual. The server might be experiencing high load.');
    }
    
    window.requestStartTime = null;
  }
}

// ==================== ENHANCED VOICE MANAGEMENT ====================

async function loadAvailableVoices() {
  try {
    const response = await makeRobustAPICall('http://127.0.0.1:8000/voices');
    
    if (response.error) {
      console.warn('Could not load voices:', response.error_message);
      return;
    }
    
    const voiceSelect = document.getElementById('voice-select');
    if (voiceSelect && response.voices) {
      voiceSelect.innerHTML = '<option value="en-US-natalie">Default Voice</option>';
      
      response.voices.forEach(voice => {
        const option = document.createElement('option');
        option.value = voice.id || voice.voiceId;
        option.textContent = `${voice.name} (${voice.language || voice.lang})`;
        voiceSelect.appendChild(option);
      });
    }
    
  } catch (error) {
    console.warn('Failed to load available voices:', error);
  }
}

// ==================== ACCESSIBILITY FEATURES ====================

// Add ARIA labels and screen reader support
function enhanceAccessibility() {
  const startButton = document.getElementById('start-recording');
  const stopButton = document.getElementById('stop-recording');
  const textInput = document.getElementById('text-input');
  
  if (startButton) {
    startButton.setAttribute('aria-label', 'Start voice recording');
    startButton.setAttribute('role', 'button');
  }
  
  if (stopButton) {
    stopButton.setAttribute('aria-label', 'Stop voice recording');
    stopButton.setAttribute('role', 'button');
  }
  
  if (textInput) {
    textInput.setAttribute('aria-label', 'Type your message here');
    textInput.setAttribute('placeholder', 'Type your message or use voice recording...');
  }
}

// ==================== OFFLINE SUPPORT ====================

// Cache management for offline functionality
const CACHE_NAME = 'robust-voice-chat-v1';
const OFFLINE_URLS = [
  '/',
  '/static/index.html',
  '/static/style.css'
];

// Register service worker for offline support
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('SW registered: ', registration);
      })
      .catch(registrationError => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Handle offline/online events
function handleOfflineMode() {
  if (!navigator.onLine) {
    showError('You are currently offline. Some features may not work.', 'network_error');
    
    // Disable network-dependent features
    const networkButtons = document.querySelectorAll('[data-requires-network]');
    networkButtons.forEach(button => {
      button.disabled = true;
      button.title = 'This feature requires an internet connection';
    });
  } else {
    hideError();
    
    // Re-enable network-dependent features
    const networkButtons = document.querySelectorAll('[data-requires-network]');
    networkButtons.forEach(button => {
      button.disabled = false;
      button.title = '';
    });
  }
}

// ==================== ANALYTICS AND DEBUGGING ====================

// Simple analytics for debugging
const analytics = {
  sessionStart: Date.now(),
  interactions: {
    recordings: 0,
    textMessages: 0,
    errors: 0,
    retries: 0
  },
  
  track(event, data = {}) {
    console.log(`[Analytics] ${event}:`, data);
    
    if (event === 'recording_started') {
      this.interactions.recordings++;
    } else if (event === 'text_message_sent') {
      this.interactions.textMessages++;
    } else if (event === 'error_occurred') {
      this.interactions.errors++;
    } else if (event === 'retry_attempted') {
      this.interactions.retries++;
    }
  },
  
  getSessionSummary() {
    const sessionDuration = Date.now() - this.sessionStart;
    return {
      duration: sessionDuration,
      interactions: this.interactions,
      errorRate: this.interactions.errors / (this.interactions.recordings + this.interactions.textMessages) || 0
    };
  }
};

// ==================== FINAL INITIALIZATION ====================

// Enhanced initialization with error handling
function initializeApplication() {
  try {
    console.log('🚀 Initializing Robust Voice Chat Application...');
    
    // Load available voices
    loadAvailableVoices();
    
    // Enhance accessibility
    enhanceAccessibility();
    
    // Handle offline mode
    handleOfflineMode();
    
    // Track session start
    analytics.track('session_started');
    
    // Update status
    updateStatus('🟢 Application ready!', 'success');
    
    console.log('✅ Application initialized successfully');
    
  } catch (error) {
    console.error('❌ Application initialization failed:', error);
    showError('Application failed to initialize properly. Some features may not work.', 'general_failure');
  }
}

// Enhanced DOM ready handler
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(initializeApplication, 500);
});

// ==================== CLEANUP AND ERROR PREVENTION ====================

// Cleanup function for page unload
window.addEventListener('beforeunload', () => {
  // Stop any ongoing recordings
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
  
  // Stop all audio playback
  document.querySelectorAll('audio').forEach(audio => {
    audio.pause();
    audio.currentTime = 0;
  });
  
  // Log session summary
  console.log('Session Summary:', analytics.getSessionSummary());
});

// ==================== EXPORT FOR TESTING ====================

// Export functions for testing purposes (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    makeRobustAPICall,
    handleAPIResponse,
    showError,
    hideError,
    analytics
  };
}

console.log('🎯 Robust Voice Chat Client loaded successfully!');