// // Enhanced Voice Chat Client with Seamless Audio Streaming
// // Integrated and optimized for immediate functionality

// // Global variables
// let mediaRecorder;
// let audioChunks = [];
// let recordedBlob;
// let currentSessionId = '';
// let autoRecordEnabled = false;
// let isWaitingForResponse = false;
// let isRecording = false;
// let retryCount = 0;
// const MAX_RETRIES = 3;

// // Server configuration
// const SERVER_BASE_URL = 'http://127.0.0.1:8000';

// // Error handling configuration
// const ERROR_CONFIG = {
//   showNotifications: true,
//   playErrorSounds: true,
//   autoRetry: true,
//   fallbackAudioEnabled: true
// };

// // Enhanced Audio Streaming Variables
// let audioContext;
// let isPlayingStreaming = false;
// let audioChunkQueue = [];
// let currentlyPlaying = false;
// let nextPlayTime = 0;
// let audioGainNode;

// // Initialize audio context immediately
// async function initStreamingAudio() {
//     if (!audioContext) {
//         try {
//             audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
//             // Create master gain node for volume control
//             audioGainNode = audioContext.createGain();
//             audioGainNode.connect(audioContext.destination);
//             audioGainNode.gain.value = 0.8; // 80% volume
            
//             console.log('Audio context initialized:', audioContext.sampleRate, 'Hz');
            
//             // Resume if suspended
//             if (audioContext.state === 'suspended') {
//                 await audioContext.resume();
//                 console.log('Audio context resumed');
//             }
            
//         } catch (error) {
//             console.error('Failed to initialize audio context:', error);
//             return null;
//         }
//     }
//     return audioContext;
// }

// // Enhanced audio chunk playback with better timing
// async function playAudioChunk(base64Audio, sequence = 0) {
//     try {
//         const ctx = await initStreamingAudio();
//         if (!ctx) {
//             console.error('Audio context not available');
//             return;
//         }

//         if (!base64Audio || base64Audio.length === 0) {
//             console.warn('Empty audio chunk, skipping sequence:', sequence);
//             return;
//         }

//         // Decode base64 to binary
//         let binaryString;
//         try {
//             binaryString = atob(base64Audio);
//         } catch (e) {
//             console.error('Failed to decode base64 audio:', e);
//             return;
//         }

//         const bytes = new Uint8Array(binaryString.length);
//         for (let i = 0; i < binaryString.length; i++) {
//             bytes[i] = binaryString.charCodeAt(i);
//         }

//         // Decode audio buffer
//         let audioBuffer;
//         try {
//             audioBuffer = await ctx.decodeAudioData(bytes.buffer.slice());
//         } catch (e) {
//             console.error('Failed to decode audio data:', e);
//             // Try fallback playback
//             playAudioFallback(base64Audio);
//             return;
//         }
        
//         // Add to queue with sequence info
//         const chunkData = {
//             buffer: audioBuffer,
//             sequence: sequence,
//             duration: audioBuffer.duration
//         };
        
//         audioChunkQueue.push(chunkData);

//         // Sort queue by sequence to handle out-of-order chunks
//         audioChunkQueue.sort((a, b) => a.sequence - b.sequence);

//         console.log(`Audio chunk ${sequence} queued, duration: ${audioBuffer.duration.toFixed(3)}s, queue size: ${audioChunkQueue.length}`);

//         // Start playback if not already playing
//         if (!currentlyPlaying) {
//             playNextChunk();
//         }

//     } catch (error) {
//         console.error('Audio chunk error:', error);
//         playAudioFallback(base64Audio);
//     }
// }

// // Enhanced playback chain with seamless transitions
// function playNextChunk() {
//     if (audioChunkQueue.length === 0) {
//         currentlyPlaying = false;
//         console.log('Audio queue empty, playback stopped');
//         updateStatus('Audio playback completed', 'success');
//         return;
//     }

//     try {
//         const ctx = audioContext;
//         const chunk = audioChunkQueue.shift();
//         const source = ctx.createBufferSource();
//         source.buffer = chunk.buffer;

//         // Connect to gain node for volume control
//         source.connect(audioGainNode);

//         // Calculate when to start this chunk for seamless playback
//         const now = ctx.currentTime;
//         const startTime = Math.max(now + 0.02, nextPlayTime); // 20ms buffer

//         source.start(startTime);
//         currentlyPlaying = true;

//         // Update next play time for gapless playback
//         nextPlayTime = startTime + chunk.buffer.duration - 0.01; // Small overlap to prevent gaps

//         console.log(`Playing chunk ${chunk.sequence} at ${startTime.toFixed(3)}s, duration: ${chunk.buffer.duration.toFixed(3)}s`);

//         // Handle playback completion
//         source.onended = () => {
//             console.log(`Chunk ${chunk.sequence} finished`);
//             // Immediately try to play next chunk
//             setTimeout(() => playNextChunk(), 1);
//         };

//         // Handle playback errors
//         source.onerror = (error) => {
//             console.error(`Chunk ${chunk.sequence} playback error:`, error);
//             setTimeout(() => playNextChunk(), 10);
//         };
        
//     } catch (error) {
//         console.error('Playback error:', error);
//         // Try next chunk
//         setTimeout(() => playNextChunk(), 10);
//     }
// }

// // Enhanced fallback audio with better error handling
// function playAudioFallback(base64Audio) {
//     try {
//         console.log('Using HTML5 audio fallback');
        
//         const binaryString = atob(base64Audio);
//         const bytes = new Uint8Array(binaryString.length);
//         for (let i = 0; i < binaryString.length; i++) {
//             bytes[i] = binaryString.charCodeAt(i);
//         }
        
//         const blob = new Blob([bytes], { type: 'audio/wav' });
//         const audioUrl = URL.createObjectURL(blob);
//         const audio = new Audio(audioUrl);
        
//         audio.volume = 0.8;
//         audio.preload = 'auto';
        
//         audio.play().then(() => {
//             console.log('Fallback audio playing');
//         }).catch(e => {
//             console.error('Fallback audio failed:', e);
//             showError('Audio playback failed');
//         });
        
//         // Cleanup
//         audio.onended = () => {
//             URL.revokeObjectURL(audioUrl);
//         };
        
//     } catch (error) {
//         console.error('Fallback audio error:', error);
//     }
// }

// // Stop all audio playback
// function stopAllAudio() {
//     console.log('Stopping all audio playback');
    
//     // Clear queue
//     audioChunkQueue = [];
//     currentlyPlaying = false;
//     nextPlayTime = 0;
    
//     // Stop any HTML5 audio
//     const audioElements = document.querySelectorAll('audio');
//     audioElements.forEach(audio => {
//         try {
//             audio.pause();
//             audio.currentTime = 0;
//         } catch (e) {
//             console.warn('Error stopping audio element:', e);
//         }
//     });
    
//     // Stop specific audio element
//     const responseAudio = getElementById(UI_ELEMENTS.responseAudio);
//     if (responseAudio) {
//         try {
//             responseAudio.pause();
//             responseAudio.currentTime = 0;
//         } catch (e) {
//             console.warn('Error stopping response audio:', e);
//         }
//     }
// }

// // Enhanced streaming response handler
// async function handleStreamingResponse(response) {
//     const contentType = response.headers.get('content-type');
    
//     if (contentType && contentType.includes('text/event-stream')) {
//         const reader = response.body.getReader();
//         const decoder = new TextDecoder();
        
//         updateStatus('Receiving audio stream...', 'processing');
//         isPlayingStreaming = true;
        
//         // Reset audio state
//         stopAllAudio();
//         audioChunkQueue = [];
//         currentlyPlaying = false;
//         nextPlayTime = 0;
        
//         try {
//             let buffer = '';
//             let chunkCount = 0;
            
//             while (true) {
//                 const { done, value } = await reader.read();
//                 if (done) {
//                     console.log('Stream ended, total chunks processed:', chunkCount);
//                     break;
//                 }
                
//                 buffer += decoder.decode(value, { stream: true });
//                 const lines = buffer.split('\n');
//                 buffer = lines.pop() || ''; // Keep incomplete line
                
//                 for (const line of lines) {
//                     if (line.startsWith('data: ')) {
//                         try {
//                             const data = JSON.parse(line.slice(6));
//                             await processStreamEvent(data);
//                             if (data.type === 'audio_chunk') {
//                                 chunkCount++;
//                             }
//                         } catch (e) {
//                             console.warn('Parse error:', e, 'Line:', line.substring(0, 100));
//                         }
//                     }
//                 }
//             }
//         } catch (error) {
//             console.error('Stream reading error:', error);
//             showError('Stream connection lost: ' + error.message);
//         } finally {
//             isPlayingStreaming = false;
//         }
//     } else {
//         // Fallback to regular JSON response
//         try {
//             const result = await response.json();
//             await handleAPIResponse(result);
//         } catch (error) {
//             console.error('Response parsing error:', error);
//             showError('Failed to parse server response');
//         }
//     }
// }

// // Enhanced stream event processing
// async function processStreamEvent(data) {
//     switch (data.type) {
//         case 'audio_chunk':
//             if (data.audio_data && data.audio_data.length > 0) {
//                 await playAudioChunk(data.audio_data, data.sequence || 0);
//             }
//             if (data.is_final) {
//                 console.log('Final audio chunk received');
//                 // Wait a bit for queue to finish
//                 setTimeout(() => {
//                     if (!currentlyPlaying && audioChunkQueue.length === 0) {
//                         handleStreamComplete();
//                     }
//                 }, 1000);
//             }
//             break;
            
//         case 'transcript':
//             console.log('Transcript:', data.text);
//             if (data.role === 'user') {
//                 addMessageToChat('user', data.text);
//             }
//             break;
            
//         case 'llm_response':
//             console.log('LLM Response:', data.text);
//             addMessageToChat('assistant', data.text);
//             break;
            
//         case 'complete':
//             console.log('Stream marked as complete');
//             handleStreamComplete();
//             break;
            
//         case 'error':
//             console.error('Stream error:', data.message);
//             showError(data.message);
//             handleStreamComplete();
//             break;
            
//         default:
//             console.log('Unknown stream event:', data.type, data);
//     }
// }

// // Handle stream completion
// function handleStreamComplete() {
//     updateStatus('Response completed!', 'success');
//     isWaitingForResponse = false;
//     updateProcessingUI(false);
    
//     // Auto-record if enabled
//     if (autoRecordEnabled && !isWaitingForResponse) {
//         setTimeout(() => {
//             if (!isWaitingForResponse && !isRecording) {
//                 startRecording();
//             }
//         }, 1500);
//     }
// }

// // Enhanced UI elements mapping
// const UI_ELEMENTS = {
//   currentSession: 'current-session',
//   conversationTurns: 'conversation-turns',
//   totalMessages: 'total-messages',
//   mainRecordButton: 'main-record-button',
//   recordStatusText: 'record-status-text',
//   sendTextButton: 'send-text-button',
//   textInput: 'text-input',
//   voiceSelect: 'voice-select',
//   statusDisplay: 'status-display',
//   autoRecordToggle: 'auto-record-toggle',
//   historyMessages: 'history-messages',
//   newSessionBtn: 'new-session-btn',
//   clearHistoryBtn: 'clear-history-btn',
//   loadSessionBtn: 'load-session-btn',
//   customSessionInput: 'custom-session-input',
//   errorContainer: 'error-container',
//   warningContainer: 'warning-container',
//   serverStatus: 'server-status',
//   responseAudio: 'response-audio'
// };

// // Initialize when page loads
// document.addEventListener("DOMContentLoaded", () => {
//   console.log('Enhanced Voice Chat Client initializing...');
  
//   initializeSession();
//   setupEventListeners();
//   setupErrorHandling();
//   checkServerHealth();
//   enhanceAccessibility();
//   handleOfflineMode();
//   setupKeyboardShortcuts();
  
//   console.log('Voice Chat Client loaded successfully!');
// });

// // Event Listeners Setup
// function setupEventListeners() {
//   console.log('Setting up event listeners...');
  
//   // Session management
//   const newSessionBtn = getElementById(UI_ELEMENTS.newSessionBtn);
//   const clearHistoryBtn = getElementById(UI_ELEMENTS.clearHistoryBtn);
//   const loadSessionBtn = getElementById(UI_ELEMENTS.loadSessionBtn);
  
//   if (newSessionBtn) newSessionBtn.addEventListener('click', createNewSession);
//   if (clearHistoryBtn) clearHistoryBtn.addEventListener('click', clearCurrentSession);
//   if (loadSessionBtn) loadSessionBtn.addEventListener('click', loadCustomSession);
  
//   // Main record button (unified start/stop)
//   const mainRecordButton = getElementById(UI_ELEMENTS.mainRecordButton);
//   if (mainRecordButton) {
//     mainRecordButton.addEventListener('click', toggleRecording);
//     console.log('Record button listener added');
//   } else {
//     console.error('Main record button not found!');
//   }
  
//   // Text input and send
//   const sendTextButton = getElementById(UI_ELEMENTS.sendTextButton);
//   const textInput = getElementById(UI_ELEMENTS.textInput);
  
//   if (sendTextButton) sendTextButton.addEventListener('click', sendToAI);
//   if (textInput) {
//     textInput.addEventListener('keydown', handleTextInputKeydown);
//     textInput.addEventListener('input', handleTextInputChange);
//   }
  
//   // Auto-record toggle
//   const autoRecordToggle = getElementById(UI_ELEMENTS.autoRecordToggle);
//   if (autoRecordToggle) autoRecordToggle.addEventListener('click', toggleAutoRecord);
  
//   // Voice selection
//   const voiceSelect = getElementById(UI_ELEMENTS.voiceSelect);
//   if (voiceSelect) voiceSelect.addEventListener('change', handleVoiceChange);
  
//   console.log('Event listeners setup complete');
// }

// // Enhanced Recording Toggle
// function toggleRecording() {
//   console.log('Toggle recording called. Current state:', isRecording, 'Waiting for response:', isWaitingForResponse);
  
//   if (isWaitingForResponse) {
//     showWarning('Please wait for the current response to complete', 3000);
//     return;
//   }

//   if (!isRecording) {
//     startRecording();
//   } else {
//     stopRecording();
//   }
// }

// // Enhanced Recording Start
// async function startRecording() {
//   console.log('Starting recording...');
  
//   try {
//     // Check if browser supports getUserMedia
//     if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
//       throw new Error('Your browser does not support audio recording');
//     }

//     // Check for microphone permissions first
//     const permissions = await navigator.permissions.query({ name: 'microphone' });
//     console.log('Microphone permission state:', permissions.state);
    
//     if (permissions.state === 'denied') {
//       showError('Microphone access denied. Please enable microphone permissions in your browser settings.');
//       return;
//     }

//     const stream = await navigator.mediaDevices.getUserMedia({ 
//       audio: {
//         echoCancellation: true,
//         noiseSuppression: true,
//         autoGainControl: true,
//         channelCount: 1,
//         sampleRate: 16000
//       } 
//     });
    
//     console.log('Microphone access granted, creating MediaRecorder...');
    
//     audioChunks = [];
    
//     // Check supported MIME types
//     let mimeType = 'audio/webm;codecs=opus';
//     if (!MediaRecorder.isTypeSupported(mimeType)) {
//       mimeType = 'audio/webm';
//       if (!MediaRecorder.isTypeSupported(mimeType)) {
//         mimeType = 'audio/mp4';
//         if (!MediaRecorder.isTypeSupported(mimeType)) {
//           mimeType = ''; // Let browser choose
//         }
//       }
//     }
    
//     console.log('Using MIME type:', mimeType);
    
//     const options = mimeType ? { mimeType } : {};
//     mediaRecorder = new MediaRecorder(stream, options);
    
//     mediaRecorder.ondataavailable = (event) => {
//       console.log('Data available:', event.data.size, 'bytes');
//       if (event.data.size > 0) {
//         audioChunks.push(event.data);
//       }
//     };
    
//     mediaRecorder.onstop = async () => {
//       console.log('MediaRecorder stopped');
//       try {
//         recordedBlob = new Blob(audioChunks, { type: mimeType || 'audio/webm' });
//         console.log('Recorded blob size:', recordedBlob.size);
        
//         if (recordedBlob.size === 0) {
//           showError('No audio was recorded. Please try again.');
//           return;
//         }
        
//         const voiceId = getElementById(UI_ELEMENTS.voiceSelect)?.value || 'en-US-natalie';
//         await transcribeAndProcess(recordedBlob, voiceId);
        
//       } catch (error) {
//         console.error('Error processing recording:', error);
//         showError('Failed to process recording: ' + error.message);
//       } finally {
//         // Stop all tracks to release microphone
//         stream.getTracks().forEach(track => {
//           track.stop();
//           console.log('Track stopped');
//         });
//       }
//     };
    
//     mediaRecorder.onerror = (event) => {
//       console.error('MediaRecorder error:', event.error);
//       showError('Recording failed: ' + (event.error?.message || 'Unknown error'));
//     };
    
//     mediaRecorder.start(1000); // Collect data every second
//     console.log('MediaRecorder started');
    
//     updateRecordingUI(true);
//     updateStatus('Recording...', 'recording');
    
//     // Add visual feedback
//     addRecordingVisualFeedback();
    
//   } catch (error) {
//     console.error('Failed to start recording:', error);
//     handleRecordingError(error);
//   }
// }

// // Enhanced Recording Stop
// function stopRecording() {
//   console.log('Stopping recording...');
  
//   try {
//     if (mediaRecorder && mediaRecorder.state === 'recording') {
//       mediaRecorder.stop();
//       console.log('MediaRecorder stop() called');
//       updateRecordingUI(false);
//       updateStatus('Processing recording...', 'processing');
//       removeRecordingVisualFeedback();
//     } else {
//       console.log('MediaRecorder not in recording state:', mediaRecorder?.state);
//     }
//   } catch (error) {
//     console.error('Error stopping recording:', error);
//     showError('Failed to stop recording: ' + error.message);
//   }
// }

// // Enhanced UI Update for Recording
// function updateRecordingUI(recording) {
//   console.log('Updating recording UI:', recording);
  
//   const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
//   const statusText = getElementById(UI_ELEMENTS.recordStatusText);
  
//   isRecording = recording;
  
//   if (recordButton) {
//     const icon = recordButton.querySelector('.record-icon');
    
//     if (recording) {
//       recordButton.classList.add('recording');
//       if (icon) icon.textContent = '⏹️';
//       recordButton.title = 'Click to stop recording';
//       recordButton.setAttribute('aria-label', 'Stop recording');
//       if (statusText) statusText.textContent = 'Recording... Click to stop';
//     } else {
//       recordButton.classList.remove('recording', 'processing');
//       if (icon) icon.textContent = '🎤';
//       recordButton.title = 'Click to start recording';
//       recordButton.setAttribute('aria-label', 'Start recording');
//       if (statusText) statusText.textContent = 'Click to start recording';
//     }
//   }
// }

// // Enhanced Processing UI
// function updateProcessingUI(processing) {
//   const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
  
//   if (recordButton) {
//     if (processing) {
//       recordButton.classList.add('processing');
//       recordButton.disabled = true;
//     } else {
//       recordButton.classList.remove('processing');
//       recordButton.disabled = false;
//     }
//   }
// }

// // Fixed transcription function to match backend parameter
// async function transcribeAndProcess(audioBlob, voiceId = 'en-US-natalie') {
//     console.log('Starting transcription and processing...');
    
//     try {
//         isWaitingForResponse = true;
//         updateProcessingUI(true);
        
//         updateStatus('Transcribing and processing...', 'processing');
        
//         const formData = new FormData();
//         // FIXED: Use 'audio' to match backend parameter
//         formData.append('audio', audioBlob, 'recording.webm');
//         formData.append('voiceId', voiceId);
        
//         console.log('Sending request to:', `${SERVER_BASE_URL}/agent/chat/${currentSessionId}`);
        
//         const response = await makeRobustAPICall(`${SERVER_BASE_URL}/agent/chat/${currentSessionId}`, {
//             method: 'POST',
//             body: formData,
//             timeout: 60000
//         }, false); // Don't parse as JSON, handle streaming
        
//         console.log('API Response received, status:', response.status);
        
//         if (!response.ok) {
//             throw new Error(`HTTP ${response.status}: ${response.statusText}`);
//         }
        
//         await handleStreamingResponse(response);
        
//     } catch (error) {
//         console.error('Error in transcribeAndProcess:', error);
//         handleProcessingError(error);
//     } finally {
//         isWaitingForResponse = false;
//         updateProcessingUI(false);
//     }
// }

// // Enhanced Text Message Sending with Streaming Support
// async function sendToAI() {
//   console.log('Sending text message...');
  
//   try {
//     if (isWaitingForResponse) {
//       showWarning('Please wait for the current response to complete', 3000);
//       return;
//     }

//     const textInput = getElementById(UI_ELEMENTS.textInput);
//     const text = textInput?.value?.trim();
    
//     if (!text) {
//       showError('Please enter some text to send', 3000);
//       textInput?.focus();
//       return;
//     }
    
//     isWaitingForResponse = true;
//     updateProcessingUI(true);
    
//     updateStatus('Processing your message...', 'processing');
    
//     const voiceId = getElementById(UI_ELEMENTS.voiceSelect)?.value || 'en-US-natalie';
    
//     const formData = new FormData();
//     formData.append('text', text);
//     formData.append('voiceId', voiceId);
    
//     console.log('Sending text request to:', `${SERVER_BASE_URL}/agent/chat/${currentSessionId}/text`);
    
//     const response = await makeRobustAPICall(`${SERVER_BASE_URL}/agent/chat/${currentSessionId}/text`, {
//       method: 'POST',
//       body: formData,
//       timeout: 60000
//     }, false); // Don't parse as JSON, handle streaming
    
//     console.log('Text API Response received');
//     await handleStreamingResponse(response);
    
//     // Clear text input on success
//     if (textInput) {
//       textInput.value = '';
//       handleTextInputChange(); // Update send button state
//     }
    
//   } catch (error) {
//     console.error('Error in sendToAI:', error);
//     handleProcessingError(error);
//   } finally {
//     isWaitingForResponse = false;
//     updateProcessingUI(false);
//   }
// }

// // Enhanced API Response Handling (fallback for non-streaming)
// async function handleAPIResponse(response) {
//   try {
//     console.log('Handling API Response:', response);
    
//     if (response.error) {
//       await handleErrorResponse(response);
//       return;
//     }
    
//     if (response.status === 'success' || response.status === 'success_no_audio') {
//       await handleSuccessResponse(response);
//     } else {
//       showError('Unexpected response format from server');
//     }
    
//   } catch (error) {
//     console.error('Error handling API response:', error);
//     showError('Failed to process server response: ' + error.message);
//   }
// }

// // Enhanced Success Response Handling (fallback)
// async function handleSuccessResponse(response) {
//   console.log('Handling success response...');
  
//   // Add messages to chat with animation
//   if (response.input) {
//     addMessageToChat('user', response.input);
//   }
  
//   if (response.response) {
//     addMessageToChat('assistant', response.response, response.status === 'success_no_audio');
//   }
  
//   // Play audio if available (non-streaming fallback)
//   if (response.audio_urls && response.audio_urls.length > 0) {
//     await playResponseAudio(response.audio_urls);
//   } else if (response.audio_url) {
//     await playResponseAudio([response.audio_url]);
//   } else if (response.tts_error) {
//     showWarning(response.tts_error_message || 'Audio generation failed, but here\'s the text response', 5000);
//   }
  
//   // Update session information
//   if (response.conversation_turns !== undefined) {
//     updateSessionInfo(response.conversation_turns, response.conversation_length);
//   }
  
//   updateStatus('Response completed!', 'success');
  
//   // Auto-record next message if enabled
//   if (autoRecordEnabled && !isWaitingForResponse) {
//     setTimeout(() => {
//       if (!isWaitingForResponse && !isRecording) {
//         startRecording();
//       }
//     }, 1500);
//   }
// }

// // Enhanced Error Response Handling
// async function handleErrorResponse(response) {
//   console.log('Handling error response:', response);
  
//   const errorMessage = response.error_message || 'An unexpected error occurred';
//   showError(errorMessage);
  
//   if (response.response) {
//     addMessageToChat('assistant', response.response, true);
//   }
  
//   if (response.session_id) {
//     await loadSessionHistory();
//   }
// }

// // Enhanced Audio Playback (fallback for non-streaming)
// async function playResponseAudio(audioUrls) {
//   try {
//     console.log('Playing response audio:', audioUrls.length, 'chunks');
//     updateStatus('Playing audio response...', 'processing');
    
//     const audio = getElementById(UI_ELEMENTS.responseAudio);
//     if (!audio) {
//       console.error('Audio element not found');
//       return;
//     }
    
//     for (let i = 0; i < audioUrls.length; i++) {
//       const audioUrl = audioUrls[i];
//       console.log(`Playing audio chunk ${i + 1}/${audioUrls.length}: ${audioUrl}`);
      
//       audio.src = audioUrl;
//       audio.volume = 0.8;
      
//       await new Promise((resolve, reject) => {
//         const timeoutId = setTimeout(() => {
//           reject(new Error('Audio playback timeout'));
//         }, 30000);
        
//         const cleanup = () => {
//           clearTimeout(timeoutId);
//           audio.removeEventListener('ended', onEnded);
//           audio.removeEventListener('error', onError);
//         };
        
//         const onEnded = () => {
//           cleanup();
//           resolve();
//         };
        
//         const onError = (error) => {
//           cleanup();
//           console.error('Audio playback error:', error);
//           reject(error);
//         };
        
//         audio.addEventListener('ended', onEnded, { once: true });
//         audio.addEventListener('error', onError, { once: true });
        
//         audio.play().catch(reject);
//       });
//     }
    
//     updateStatus('Audio playback completed', 'success');
    
//   } catch (error) {
//     console.error('Audio playback failed:', error);
//     showWarning('Audio playback failed, but you can see the text response above', 5000);
//   }
// }

// // Enhanced Chat Message Addition
// function addMessageToChat(role, content, isError = false) {
//   const historyContainer = getElementById(UI_ELEMENTS.historyMessages);
//   if (!historyContainer) {
//     console.error('History container not found');
//     return;
//   }
  
//   console.log('Adding message to chat:', role, content.substring(0, 100) + '...');
  
//   // Remove the placeholder if it exists
//   const emptyChat = historyContainer.querySelector('.empty-chat');
//   if (emptyChat) {
//     emptyChat.remove();
//   }
  
//   const messageDiv = document.createElement('div');
//   messageDiv.className = `chat-message ${role} ${isError ? 'error' : ''}`;
  
//   const time = new Date().toLocaleTimeString();
//   const errorIndicator = isError ? '<span class="error-indicator" title="This message had issues">⚠️</span>' : '';
  
//   messageDiv.innerHTML = `
//     <div class="message-content">${errorIndicator}${escapeHtml(content)}</div>
//     <div class="message-time">${time}</div>
//   `;
  
//   historyContainer.appendChild(messageDiv);
  
//   // Smooth scroll to bottom
//   setTimeout(() => {
//     historyContainer.scrollTo({
//       top: historyContainer.scrollHeight,
//       behavior: 'smooth'
//     });
//   }, 100);
// }

// // Enhanced Status Update
// function updateStatus(message, type = 'info') {
//   const statusElement = getElementById(UI_ELEMENTS.statusDisplay);
//   if (!statusElement) return;
  
//   console.log('Status update:', message, type);
  
//   const iconElement = statusElement.querySelector('.status-icon');
//   const textElement = statusElement.querySelector('.status-text');
  
//   if (textElement) {
//     textElement.textContent = message.replace(/^[🟢🔴🟡⚠️🔄🎤⏹️📤🔊✅❌]+ ?/, '');
//   }
  
//   if (iconElement) {
//     const iconMap = {
//       'info': '🟢',
//       'recording': '🎤',
//       'processing': '🔄',
//       'success': '✅',
//       'error': '❌',
//       'warning': '⚠️'
//     };
//     iconElement.textContent = iconMap[type] || '🟢';
//   }
  
//   statusElement.className = `status-display ${type}`;
// }

// // Session Management
// function initializeSession() {
//   console.log('Initializing session...');
  
//   const urlParams = new URLSearchParams(window.location.search);
//   const sessionFromUrl = urlParams.get('session');
  
//   if (sessionFromUrl && sessionFromUrl.length > 0) {
//     currentSessionId = sessionFromUrl;
//   } else {
//     currentSessionId = generateSessionId();
//     updateURL();
//   }
  
//   const currentSessionElement = getElementById(UI_ELEMENTS.currentSession);
//   if (currentSessionElement) {
//     currentSessionElement.textContent = currentSessionId;
//   }
  
//   console.log('Session initialized:', currentSessionId);
//   loadSessionHistory();
// }

// function generateSessionId() {
//   const timestamp = Date.now();
//   const random = Math.random().toString(36).substr(2, 9);
//   return `session-${timestamp}-${random}`;
// }

// function updateURL() {
//   const newUrl = `${window.location.pathname}?session=${currentSessionId}`;
//   window.history.replaceState({}, '', newUrl);
// }

// async function loadSessionHistory() {
//   try {
//     console.log('Loading session history for:', currentSessionId);
    
//     const data = await makeRobustAPICall(`${SERVER_BASE_URL}/agent/history/${currentSessionId}`, {
//       timeout: 10000
//     });
    
//     console.log('Session history loaded:', data);
    
//     if (data.status === 'success') {
//       updateSessionInfo(data.conversation_turns, data.message_count);
//       displayChatHistory(data.history);
//     }
//   } catch (error) {
//     console.error('Failed to load session history:', error);
//     showWarning('Could not load conversation history', 5000);
//   }
// }

// function updateSessionInfo(turns, messages) {
//   const turnsElement = getElementById(UI_ELEMENTS.conversationTurns);
//   const messagesElement = getElementById(UI_ELEMENTS.totalMessages);
  
//   if (turnsElement) turnsElement.textContent = turns || 0;
//   if (messagesElement) messagesElement.textContent = messages || 0;
// }

// function displayChatHistory(history) {
//   const historyContainer = getElementById(UI_ELEMENTS.historyMessages);
//   if (!historyContainer) return;
  
//   historyContainer.innerHTML = '';
  
//   if (!history || history.length === 0) {
//     historyContainer.innerHTML = `
//       <div class="empty-chat">
//         <div class="empty-icon">💭</div>
//         <p>Start a conversation by recording or typing a message</p>
//       </div>
//     `;
//     return;
//   }
  
//   console.log('Displaying chat history:', history.length, 'messages');
  
//   history.forEach((message, index) => {
//     setTimeout(() => {
//       const messageDiv = document.createElement('div');
//       messageDiv.className = `chat-message ${message.role}`;
      
//       const time = new Date(message.timestamp * 1000).toLocaleTimeString();
//       messageDiv.innerHTML = `
//         <div class="message-content">${escapeHtml(message.content)}</div>
//         <div class="message-time">${time}</div>
//       `;
      
//       historyContainer.appendChild(messageDiv);
//     }, index * 50); // Staggered animation
//   });
  
//   setTimeout(() => {
//     historyContainer.scrollTop = historyContainer.scrollHeight;
//   }, history.length * 50 + 100);
// }

// function createNewSession() {
//   console.log('Creating new session...');
  
//   currentSessionId = generateSessionId();
//   const currentSessionElement = getElementById(UI_ELEMENTS.currentSession);
//   if (currentSessionElement) {
//     currentSessionElement.textContent = currentSessionId;
//   }
  
//   updateURL();
  
//   updateSessionInfo(0, 0);
//   const historyContainer = getElementById(UI_ELEMENTS.historyMessages);
//   if (historyContainer) {
//     historyContainer.innerHTML = `
//       <div class="empty-chat">
//         <div class="empty-icon">💭</div>
//         <p>Start a conversation by recording or typing a message</p>
//       </div>
//     `;
//   }
//   updateStatus('New session created!', 'success');
// }

// async function clearCurrentSession() {
//   try {
//     console.log('Clearing current session...');
    
//     const response = await makeRobustAPICall(`${SERVER_BASE_URL}/agent/history/${currentSessionId}`, {
//       method: 'DELETE',
//       timeout: 10000
//     });
    
//     console.log('Clear session response:', response);
    
//     if (response.error) {
//       showError(response.error_message || 'Failed to clear session');
//       return;
//     }
    
//     updateSessionInfo(0, 0);
//     const historyContainer = getElementById(UI_ELEMENTS.historyMessages);
//     if (historyContainer) {
//       historyContainer.innerHTML = `
//         <div class="empty-chat">
//           <div class="empty-icon">💭</div>
//           <p>Start a conversation by recording or typing a message</p>
//         </div>
//       `;
//     }
//     updateStatus('Session history cleared!', 'success');
    
//   } catch (error) {
//     console.error('Failed to clear session:', error);
//     showError('Failed to clear session history: ' + error.message);
//   }
// }

// function loadCustomSession() {
//   const customSessionInput = getElementById(UI_ELEMENTS.customSessionInput);
//   const sessionId = customSessionInput?.value?.trim();
  
//   if (!sessionId) {
//     showError('Please enter a session ID', 3000);
//     customSessionInput?.focus();
//     return;
//   }
  
//   currentSessionId = sessionId;
//   const currentSessionElement = getElementById(UI_ELEMENTS.currentSession);
//   if (currentSessionElement) {
//     currentSessionElement.textContent = currentSessionId;
//   }
  
//   updateURL();
  
//   if (customSessionInput) customSessionInput.value = '';
//   loadSessionHistory();
//   updateStatus('Session loaded!', 'success');
// }

// // Enhanced Auto-Record Toggle
// function toggleAutoRecord() {
//   autoRecordEnabled = !autoRecordEnabled;
//   const toggle = getElementById(UI_ELEMENTS.autoRecordToggle);
//   const statusElement = toggle?.querySelector('.toggle-status');
  
//   if (toggle && statusElement) {
//     if (autoRecordEnabled) {
//       toggle.classList.add('active');
//       statusElement.textContent = 'ON';
//     } else {
//       toggle.classList.remove('active');
//       statusElement.textContent = 'OFF';
//     }
//   }
  
//   updateStatus(`Auto-record ${autoRecordEnabled ? 'enabled' : 'disabled'}`, 'info');
// }

// // Enhanced Event Handlers
// function handleTextInputKeydown(e) {
//   if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
//     e.preventDefault();
//     sendToAI();
//   }
// }

// function handleTextInputChange() {
//   const textInput = getElementById(UI_ELEMENTS.textInput);
//   const sendButton = getElementById(UI_ELEMENTS.sendTextButton);
  
//   if (textInput && sendButton) {
//     const hasText = textInput.value.trim().length > 0;
//     sendButton.disabled = !hasText || isWaitingForResponse;
//     sendButton.style.opacity = hasText && !isWaitingForResponse ? '1' : '0.5';
//   }
// }

// function handleVoiceChange() {
//   const voiceSelect = getElementById(UI_ELEMENTS.voiceSelect);
//   if (voiceSelect) {
//     const selectedVoice = voiceSelect.options[voiceSelect.selectedIndex].text;
//     updateStatus(`Voice changed to ${selectedVoice}`, 'info');
//   }
// }

// // Enhanced Error Handling
// function handleRecordingError(error) {
//   console.error('Recording error:', error);
  
//   if (error.name === 'NotAllowedError') {
//     showError('Microphone access denied. Please enable microphone permissions and try again.');
//   } else if (error.name === 'NotFoundError') {
//     showError('No microphone found. Please connect a microphone and try again.');
//   } else if (error.name === 'NotReadableError') {
//     showError('Microphone is already in use by another application.');
//   } else {
//     showError('Failed to start recording: ' + error.message);
//   }
// }

// function handleProcessingError(error) {
//   console.error('Processing error:', error);
  
//   if (error.message.includes('timeout')) {
//     showError('The request took too long. Please try with a shorter recording or message.');
//   } else if (error.message.includes('No internet') || !navigator.onLine) {
//     showError('No internet connection. Please check your network and try again.');
//   } else if (error.message.includes('Failed to fetch')) {
//     showError('Cannot connect to the server. Please make sure the server is running.');
//   } else {
//     showError('Failed to process your request: ' + error.message);
//   }
// }

// // Enhanced API Call Function with Streaming Support
// async function makeRobustAPICall(url, options = {}, parseJSON = true) {
//   console.log('Making API call to:', url);
  
//   const controller = new AbortController();
//   const timeoutId = setTimeout(() => controller.abort(), options.timeout || 30000);
  
//   let attempt = 0;
//   const maxAttempts = options.maxRetries || 1;
  
//   while (attempt < maxAttempts) {
//     try {
//       const response = await fetch(url, {
//         ...options,
//         signal: controller.signal,
//         headers: {
//           ...options.headers,
//         }
//       });
      
//       clearTimeout(timeoutId);
      
//       console.log('API response status:', response.status);
      
//       if (!response.ok) {
//         throw new Error(`HTTP ${response.status}: ${response.statusText}`);
//       }
      
//       // If we don't want to parse as JSON (for streaming), return the response directly
//       if (!parseJSON) {
//         return response;
//       }
      
//       const contentType = response.headers.get('content-type');
//       if (contentType && contentType.includes('application/json')) {
//         const data = await response.json();
//         console.log('API response data:', data);
//         return data;
//       } else {
//         const text = await response.text();
//         console.log('API response text:', text.substring(0, 200) + '...');
//         return text;
//       }
      
//     } catch (error) {
//       attempt++;
//       clearTimeout(timeoutId);
      
//       console.error(`API call attempt ${attempt} failed:`, error);
      
//       if (error.name === 'AbortError') {
//         throw new Error('Request timeout - the server is taking too long to respond');
//       }
      
//       if (!navigator.onLine) {
//         throw new Error('No internet connection');
//       }
      
//       if (attempt >= maxAttempts) {
//         throw error;
//       }
      
//       // Wait before retry
//       await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
//     }
//   }
// }

// // Enhanced Notification Functions
// function showError(message, duration = 8000) {
//   console.error('Showing error:', message);
//   updateStatus(`${message}`, 'error');
  
//   const errorContainer = getElementById(UI_ELEMENTS.errorContainer);
//   if (errorContainer) {
//     errorContainer.innerHTML = `
//       <div class="error-message">
//         <span class="error-icon">⚠️</span>
//         <span class="error-text">${escapeHtml(message)}</span>
//         <button onclick="hideError()" class="close-btn" title="Dismiss">✖️</button>
//       </div>
//     `;
//     errorContainer.style.display = 'block';
    
//     // Auto hide after duration
//     setTimeout(hideError, duration);
//   }
  
//   // Add to browser console for debugging
//   console.error('Error:', message);
// }

// function showWarning(message, duration = 6000) {
//   console.warn('Showing warning:', message);
//   updateStatus(`${message}`, 'warning');
  
//   const warningContainer = getElementById(UI_ELEMENTS.warningContainer);
//   if (warningContainer) {
//     warningContainer.innerHTML = `
//       <div class="warning-message">
//         <span class="warning-icon">⚠️</span>
//         <span class="warning-text">${escapeHtml(message)}</span>
//         <button onclick="hideWarning()" class="close-btn" title="Dismiss">✖️</button>
//       </div>
//     `;
//     warningContainer.style.display = 'block';
    
//     // Auto hide after duration
//     setTimeout(hideWarning, duration);
//   }
  
//   console.warn('Warning:', message);
// }

// function hideError() {
//   const errorContainer = getElementById(UI_ELEMENTS.errorContainer);
//   if (errorContainer) {
//     errorContainer.style.display = 'none';
//     errorContainer.innerHTML = '';
//   }
// }

// function hideWarning() {
//   const warningContainer = getElementById(UI_ELEMENTS.warningContainer);
//   if (warningContainer) {
//     warningContainer.style.display = 'none';
//     warningContainer.innerHTML = '';
//   }
// }

// // Server Health Check
// async function checkServerHealth() {
//   try {
//     console.log('Checking server health...');
    
//     const response = await makeRobustAPICall(`${SERVER_BASE_URL}/health`, {
//       method: 'GET',
//       timeout: 5000
//     });
    
//     console.log('Server health response:', response);
//     displayHealthStatus(response);
    
//     if (response.status === 'degraded') {
//       showWarning('Some services are currently unavailable. Functionality may be limited.', 10000);
//     }
    
//   } catch (error) {
//     console.error('Server health check failed:', error);
//     displayHealthStatus({ status: 'unhealthy', message: 'Server unavailable' });
//     showError('Cannot connect to the server. Please make sure it is running on ' + SERVER_BASE_URL);
//   }
// }

// function displayHealthStatus(health) {
//   const statusElement = getElementById(UI_ELEMENTS.serverStatus);
//   if (!statusElement) return;
  
//   const statusIndicator = statusElement.querySelector('.status-indicator');
//   const statusContent = statusElement.querySelector('.server-status-content span');
  
//   const statusColors = {
//     'healthy': 'var(--success-color, #22c55e)',
//     'degraded': 'var(--warning-color, #f59e0b)',
//     'unhealthy': 'var(--danger-color, #ef4444)'
//   };
  
//   if (statusIndicator) {
//     statusIndicator.style.background = statusColors[health.status] || statusColors.unhealthy;
//     statusIndicator.className = `status-indicator ${health.status}`;
//   }
  
//   if (statusContent) {
//     if (health.apis) {
//       statusContent.innerHTML = `
//         <div style="font-weight: 700; margin-bottom: 4px;">Server: ${health.status.toUpperCase()}</div>
//         <div style="font-size: 0.75rem;">
//           STT: ${health.apis.assemblyai?.status || 'Unknown'}<br>
//           LLM: ${health.apis.gemini?.status || 'Unknown'}<br>
//           TTS: ${health.apis.murf?.status || 'Unknown'}
//         </div>
//       `;
//     } else {
//       statusContent.textContent = health.message || `Server: ${health.status}`;
//     }
//   }
// }

// // Visual Feedback Functions
// function addRecordingVisualFeedback() {
//   document.body.classList.add('recording-active');
  
//   // Add pulsing effect to record button
//   const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
//   if (recordButton) {
//     recordButton.style.boxShadow = '0 0 30px rgba(239, 68, 68, 0.5)';
//   }
// }

// function removeRecordingVisualFeedback() {
//   document.body.classList.remove('recording-active');
  
//   const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
//   if (recordButton) {
//     recordButton.style.boxShadow = '';
//   }
// }

// // Keyboard Shortcuts
// function setupKeyboardShortcuts() {
//   console.log('Setting up keyboard shortcuts...');
  
//   document.addEventListener('keydown', (event) => {
//     // Prevent shortcuts when typing in inputs
//     if (['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
//       return;
//     }
    
//     switch(event.code) {
//       case 'Space':
//         event.preventDefault();
//         toggleRecording();
//         break;
        
//       case 'Escape':
//         event.preventDefault();
//         hideError();
//         hideWarning();
//         if (isRecording) {
//           stopRecording();
//         }
//         // Stop audio playback
//         stopAllAudio();
//         break;
        
//       case 'KeyN':
//         if (event.ctrlKey || event.metaKey) {
//           event.preventDefault();
//           createNewSession();
//         }
//         break;
        
//       case 'KeyC':
//         if ((event.ctrlKey || event.metaKey) && event.shiftKey) {
//           event.preventDefault();
//           clearCurrentSession();
//         }
//         break;
//     }
//   });
  
//   // Show/hide keyboard hints
//   let hintsTimeout;
//   document.addEventListener('keydown', () => {
//     const hints = document.querySelector('.floating-hints');
//     if (hints) {
//       hints.style.opacity = '1';
//       clearTimeout(hintsTimeout);
//       hintsTimeout = setTimeout(() => {
//         hints.style.opacity = '0.7';
//       }, 3000);
//     }
//   });
// }

// // Enhanced Error Handling Setup
// function setupErrorHandling() {
//   console.log('Setting up error handling...');
  
//   // Global error handler
//   window.addEventListener('error', (event) => {
//     console.error('Global error:', event.error);
//     showError('An unexpected error occurred. Please refresh the page if problems persist.');
//   });

//   // Unhandled promise rejection handler
//   window.addEventListener('unhandledrejection', (event) => {
//     console.error('Unhandled promise rejection:', event.reason);
//     showError('An unexpected error occurred. Please refresh the page if problems persist.');
//     event.preventDefault();
//   });

//   // Online/offline handlers
//   window.addEventListener('online', () => {
//     console.log('Connection restored');
//     updateStatus('Connection restored', 'success');
//     hideError();
//     checkServerHealth();
//   });

//   window.addEventListener('offline', () => {
//     console.log('Connection lost');
//     showError('No internet connection. Please check your network.');
//     updateStatus('No internet connection', 'error');
//   });
// }

// // Accessibility Enhancements
// function enhanceAccessibility() {
//   console.log('Enhancing accessibility...');
  
//   const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
//   const textInput = getElementById(UI_ELEMENTS.textInput);
  
//   if (recordButton) {
//     recordButton.setAttribute('aria-label', 'Start or stop voice recording');
//     recordButton.setAttribute('role', 'button');
//     recordButton.setAttribute('tabindex', '0');
//   }
  
//   if (textInput) {
//     textInput.setAttribute('aria-label', 'Type your message here');
//   }
  
//   // Add focus management
//   document.addEventListener('keydown', (e) => {
//     if (e.key === 'Tab') {
//       document.body.classList.add('keyboard-navigation');
//     }
//   });
  
//   document.addEventListener('mousedown', () => {
//     document.body.classList.remove('keyboard-navigation');
//   });
// }

// // Offline Mode Handling
// function handleOfflineMode() {
//   if (!navigator.onLine) {
//     showError('You are currently offline. Some features may not work.');
//   }
  
//   // Service worker registration for offline support (if available)
//   if ('serviceWorker' in navigator) {
//     navigator.serviceWorker.register('/sw.js').catch(err => {
//       console.log('Service worker registration failed:', err);
//     });
//   }
// }

// // Utility Functions
// function getElementById(id) {
//   const element = document.getElementById(id);
//   if (!element) {
//     console.warn(`Element with ID '${id}' not found`);
//   }
//   return element;
// }

// function escapeHtml(text) {
//   const map = {
//     '&': '&amp;',
//     '<': '&lt;',
//     '>': '&gt;',
//     '"': '&quot;',
//     "'": '&#039;'
//   };
//   return text.replace(/[&<>"']/g, function(m) { return map[m]; });
// }

// function debounce(func, wait) {
//   let timeout;
//   return function executedFunction(...args) {
//     const later = () => {
//       clearTimeout(timeout);
//       func(...args);
//     };
//     clearTimeout(timeout);
//     timeout = setTimeout(later, wait);
//   };
// }

// // Initialize audio context on first user interaction
// document.addEventListener('click', async function initAudioOnClick() {
//     await initStreamingAudio();
//     document.removeEventListener('click', initAudioOnClick);
// }, { once: true });

// // Also try to init on page load
// document.addEventListener('DOMContentLoaded', async () => {
//     // Try to initialize audio context (might be blocked until user interaction)
//     try {
//         await initStreamingAudio();
//     } catch (e) {
//         console.log('Audio context initialization delayed until user interaction');
//     }
// });

// // Initialize text input change handler with debouncing
// document.addEventListener('DOMContentLoaded', () => {
//   const textInput = getElementById(UI_ELEMENTS.textInput);
//   if (textInput) {
//     const debouncedHandler = debounce(handleTextInputChange, 300);
//     textInput.addEventListener('input', debouncedHandler);
//   }
// });

// // Periodic health check
// setInterval(checkServerHealth, 30000); // Check every 30 seconds

// // Export functions for global access (for onclick handlers)
// window.hideError = hideError;
// window.hideWarning = hideWarning;

// // Enhanced Debug utilities
// window.debugAudio = {
//     context: () => audioContext,
//     status: () => ({ 
//         isPlaying: currentlyPlaying, 
//         queueLength: audioChunkQueue.length,
//         nextPlayTime: nextPlayTime,
//         contextState: audioContext?.state
//     }),
//     stop: () => stopAllAudio(),
//     queue: () => audioChunkQueue,
//     test: async () => {
//         // Test with a simple beep
//         const ctx = await initStreamingAudio();
//         if (ctx) {
//             const oscillator = ctx.createOscillator();
//             const gainNode = ctx.createGain();
            
//             oscillator.connect(gainNode);
//             gainNode.connect(ctx.destination);
            
//             oscillator.frequency.value = 440; // A4 note
//             gainNode.gain.value = 0.1;
            
//             oscillator.start();
//             oscillator.stop(ctx.currentTime + 0.2);
            
//             console.log('Audio test played');
//         }
//     }
// };

// console.log('Enhanced Voice Chat Client with Seamless Audio Streaming loaded successfully!');











let mediaRecorder;
let audioChunks = [];
let recordedBlob;
let currentSessionId = '';
let autoRecordEnabled = false;
let isWaitingForResponse = false;
let isRecording = false;
let retryCount = 0;
const MAX_RETRIES = 3;

// Server configuration
const SERVER_BASE_URL = 'http://127.0.0.1:8000';

// Error handling configuration
const ERROR_CONFIG = {
  showNotifications: true,
  playErrorSounds: true,
  autoRetry: true,
  fallbackAudioEnabled: true
};

// FIXED: Enhanced Audio Streaming Variables
let audioContext;
let isPlayingStreaming = false;
let audioChunkQueue = [];
let currentlyPlaying = false;
let nextPlayTime = 0;
let audioGainNode;
let expectedSequence = 0;
let audioBufferQueue = []; // For proper sequencing
let playbackStarted = false;

// FIXED: Initialize audio context with proper error handling
async function initStreamingAudio() {
    if (!audioContext || audioContext.state === 'closed') {
        try {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (!AudioContextClass) {
                throw new Error('Web Audio API not supported');
            }
            
            audioContext = new AudioContextClass({
                sampleRate: 24000,
                latencyHint: 'playback'
            });
            
            // Create master gain node for volume control
            audioGainNode = audioContext.createGain();
            audioGainNode.connect(audioContext.destination);
            audioGainNode.gain.value = 0.8; // 80% volume
            
            console.log('Audio context initialized:', {
                sampleRate: audioContext.sampleRate,
                state: audioContext.state,
                latency: audioContext.baseLatency
            });
            
            // Resume if suspended
            if (audioContext.state === 'suspended') {
                await audioContext.resume();
                console.log('Audio context resumed');
            }
            
        } catch (error) {
            console.error('Failed to initialize audio context:', error);
            throw error;
        }
    }
    
    return audioContext;
}

// FIXED: Enhanced audio chunk playback with proper WAV handling
async function playAudioChunk(base64Audio, sequence = 0, durationMs = 0) {
    try {
        const ctx = await initStreamingAudio();
        if (!ctx || ctx.state === 'closed') {
            console.error('Audio context not available');
            return false;
        }

        if (!base64Audio || base64Audio.length === 0) {
            console.warn('Empty audio chunk, skipping sequence:', sequence);
            return false;
        }

        // Decode base64 to binary
        let binaryString;
        try {
            binaryString = atob(base64Audio);
        } catch (e) {
            console.error('Failed to decode base64 audio:', e);
            return false;
        }

        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        // FIXED: Proper WAV format validation
        if (bytes.length < 44) {
            console.error('Invalid WAV file: too short');
            return false;
        }

        // Check WAV header
        const header = new TextDecoder().decode(bytes.slice(0, 4));
        if (header !== 'RIFF') {
            console.error('Invalid WAV file: missing RIFF header');
            return false;
        }

        // Decode audio buffer with better error handling
        let audioBuffer;
        try {
            audioBuffer = await ctx.decodeAudioData(bytes.buffer.slice());
            
            if (!audioBuffer) {
                throw new Error('Failed to decode audio buffer');
            }
            
            console.log(`Audio chunk ${sequence} decoded successfully:`, {
                duration: audioBuffer.duration.toFixed(3),
                channels: audioBuffer.numberOfChannels,
                sampleRate: audioBuffer.sampleRate,
                length: audioBuffer.length
            });
            
        } catch (e) {
            console.error('Failed to decode audio data:', e);
            // Try HTML5 fallback
            playAudioFallback(base64Audio, sequence);
            return false;
        }
        
        // FIXED: Add to buffer queue with proper sequencing
        const chunkData = {
            buffer: audioBuffer,
            sequence: sequence,
            duration: audioBuffer.duration,
            expectedDuration: durationMs / 1000,
            timestamp: Date.now()
        };
        
        audioBufferQueue.push(chunkData);
        audioBufferQueue.sort((a, b) => a.sequence - b.sequence);

        console.log(`Audio chunk ${sequence} queued, buffer queue size: ${audioBufferQueue.length}`);

        // Start playback if not already playing and we have the expected sequence
        if (!currentlyPlaying && !playbackStarted) {
            startSequentialPlayback();
        }

        return true;

    } catch (error) {
        console.error('Audio chunk error:', error);
        playAudioFallback(base64Audio, sequence);
        return false;
    }
}

// FIXED: Sequential playback for seamless audio
function startSequentialPlayback() {
    if (playbackStarted) return;
    
    playbackStarted = true;
    currentlyPlaying = true;
    expectedSequence = 0;
    nextPlayTime = audioContext.currentTime + 0.1; // Small initial delay
    
    console.log('Starting sequential audio playback');
    playNextSequentialChunk();
}

// FIXED: Play chunks in sequence for gapless playback
function playNextSequentialChunk() {
    // Find the next expected chunk
    const chunkIndex = audioBufferQueue.findIndex(chunk => chunk.sequence === expectedSequence);
    
    if (chunkIndex === -1) {
        // Expected chunk not available yet, wait a bit
        if (audioBufferQueue.length > 0) {
            console.log(`Waiting for chunk ${expectedSequence}, have chunks:`, audioBufferQueue.map(c => c.sequence));
            setTimeout(() => playNextSequentialChunk(), 50);
        } else {
            // No more chunks available
            console.log('No more audio chunks, stopping playback');
            stopSequentialPlayback();
        }
        return;
    }
    
    try {
        const chunk = audioBufferQueue.splice(chunkIndex, 1)[0];
        const source = audioContext.createBufferSource();
        source.buffer = chunk.buffer;
        source.connect(audioGainNode);

        // Calculate precise timing for gapless playback
        const now = audioContext.currentTime;
        const startTime = Math.max(now + 0.01, nextPlayTime);
        
        source.start(startTime);
        
        // Update timing for next chunk
        nextPlayTime = startTime + chunk.buffer.duration;
        expectedSequence++;

        console.log(`Playing chunk ${chunk.sequence} at ${startTime.toFixed(3)}s, duration: ${chunk.buffer.duration.toFixed(3)}s, next: ${nextPlayTime.toFixed(3)}s`);

        // Handle completion and errors
        source.onended = () => {
            console.log(`Chunk ${chunk.sequence} finished`);
            // Try to play next chunk immediately
            setTimeout(() => playNextSequentialChunk(), 1);
        };

        source.onerror = (error) => {
            console.error(`Chunk ${chunk.sequence} playback error:`, error);
            setTimeout(() => playNextSequentialChunk(), 10);
        };
        
    } catch (error) {
        console.error('Playback error:', error);
        setTimeout(() => playNextSequentialChunk(), 10);
    }
}

// Stop sequential playback
function stopSequentialPlayback() {
    playbackStarted = false;
    currentlyPlaying = false;
    expectedSequence = 0;
    nextPlayTime = 0;
    console.log('Sequential playback stopped');
}

// FIXED: Enhanced fallback audio with proper sequencing
function playAudioFallback(base64Audio, sequence = 0) {
    try {
        console.log(`Using HTML5 audio fallback for chunk ${sequence}`);
        
        const binaryString = atob(base64Audio);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        const blob = new Blob([bytes], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        
        audio.volume = 0.8;
        audio.preload = 'auto';
        
        // Add delay based on sequence for proper ordering
        const delay = sequence * 50; // 50ms per sequence
        
        setTimeout(() => {
            audio.play().then(() => {
                console.log(`Fallback audio chunk ${sequence} playing`);
            }).catch(e => {
                console.error(`Fallback audio chunk ${sequence} failed:`, e);
            });
        }, delay);
        
        // Cleanup
        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
            console.log(`Fallback audio chunk ${sequence} ended`);
        };
        
        audio.onerror = (error) => {
            console.error(`Fallback audio chunk ${sequence} error:`, error);
            URL.revokeObjectURL(audioUrl);
        };
        
    } catch (error) {
        console.error('Fallback audio error:', error);
    }
}

// FIXED: Stop all audio playback
function stopAllAudio() {
    console.log('Stopping all audio playback');
    
    // Clear queues and reset state
    audioBufferQueue = [];
    audioChunkQueue = [];
    stopSequentialPlayback();
    
    // Stop any HTML5 audio
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach(audio => {
        try {
            audio.pause();
            audio.currentTime = 0;
        } catch (e) {
            console.warn('Error stopping audio element:', e);
        }
    });
    
    // Stop specific audio element
    const responseAudio = getElementById(UI_ELEMENTS.responseAudio);
    if (responseAudio) {
        try {
            responseAudio.pause();
            responseAudio.currentTime = 0;
        } catch (e) {
            console.warn('Error stopping response audio:', e);
        }
    }
    
    updateStatus('Audio playback stopped', 'info');
}

// FIXED: Enhanced streaming response handler
async function handleStreamingResponse(response) {
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('text/event-stream')) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        updateStatus('Receiving audio stream...', 'processing');
        isPlayingStreaming = true;
        
        // Reset audio state
        stopAllAudio();
        audioBufferQueue = [];
        expectedSequence = 0;
        playbackStarted = false;
        
        try {
            let buffer = '';
            let chunkCount = 0;
            let audioConfigReceived = false;
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    console.log('Stream ended, total chunks processed:', chunkCount);
                    break;
                }
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep incomplete line
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            await processStreamEvent(data);
                            
                            if (data.type === 'audio_config') {
                                audioConfigReceived = true;
                            } else if (data.type === 'audio_chunk' && audioConfigReceived) {
                                chunkCount++;
                            }
                        } catch (e) {
                            console.warn('Parse error:', e, 'Line:', line.substring(0, 100));
                        }
                    }
                }
            }
            
            // Give a moment for final chunks to play
            setTimeout(() => {
                if (!currentlyPlaying && audioBufferQueue.length === 0) {
                    handleStreamComplete();
                }
            }, 2000);
            
        } catch (error) {
            console.error('Stream reading error:', error);
            showError('Stream connection lost: ' + error.message);
        } finally {
            isPlayingStreaming = false;
        }
    } else {
        // Fallback to regular JSON response
        try {
            const result = await response.json();
            await handleAPIResponse(result);
        } catch (error) {
            console.error('Response parsing error:', error);
            showError('Failed to parse server response');
        }
    }
}

// FIXED: Enhanced stream event processing
async function processStreamEvent(data) {
    switch (data.type) {
        case 'audio_config':
            console.log('Audio config received:', data);
            // Reset audio state when new stream starts
            stopAllAudio();
            audioBufferQueue = [];
            expectedSequence = 0;
            playbackStarted = false;
            
            // Initialize audio context with config
            try {
                await initStreamingAudio();
                updateStatus('Audio stream ready', 'processing');
            } catch (error) {
                console.error('Failed to initialize audio with config:', error);
                showError('Audio initialization failed');
            }
            break;
            
        case 'audio_chunk':
            if (data.audio_data && data.audio_data.length > 0) {
                const success = await playAudioChunk(
                    data.audio_data, 
                    data.sequence || 0, 
                    data.duration_ms || 0
                );
                
                if (success) {
                    updateStatus(`Playing audio (${data.sequence || 0})`, 'processing');
                }
            }
            
            if (data.is_final) {
                console.log('Final audio chunk received');
                // Mark the end and let sequential playback finish naturally
                setTimeout(() => {
                    if (!currentlyPlaying && audioBufferQueue.length === 0) {
                        handleStreamComplete();
                    }
                }, 3000);
            }
            break;
            
        case 'transcript':
            console.log('Transcript:', data.text);
            if (data.role === 'user') {
                addMessageToChat('user', data.text);
            }
            break;
            
        case 'llm_response':
            console.log('LLM Response:', data.text);
            addMessageToChat('assistant', data.text);
            break;
            
        case 'complete':
            console.log('Stream marked as complete');
            handleStreamComplete();
            break;
            
        case 'error':
            console.error('Stream error:', data.message);
            showError(data.message);
            handleStreamComplete();
            break;
            
        default:
            console.log('Unknown stream event:', data.type, data);
    }
}

// FIXED: Handle stream completion
function handleStreamComplete() {
    updateStatus('Response completed!', 'success');
    isWaitingForResponse = false;
    updateProcessingUI(false);
    
    // Stop any remaining playback after a delay
    setTimeout(() => {
        if (audioBufferQueue.length === 0 && !currentlyPlaying) {
            stopSequentialPlayback();
        }
    }, 1000);
    
    // Auto-record if enabled
    if (autoRecordEnabled && !isWaitingForResponse) {
        setTimeout(() => {
            if (!isWaitingForResponse && !isRecording) {
                startRecording();
            }
        }, 2000);
    }
}

// Enhanced UI elements mapping
const UI_ELEMENTS = {
  currentSession: 'current-session',
  conversationTurns: 'conversation-turns',
  totalMessages: 'total-messages',
  mainRecordButton: 'main-record-button',
  recordStatusText: 'record-status-text',
  sendTextButton: 'send-text-button',
  textInput: 'text-input',
  voiceSelect: 'voice-select',
  statusDisplay: 'status-display',
  autoRecordToggle: 'auto-record-toggle',
  historyMessages: 'history-messages',
  newSessionBtn: 'new-session-btn',
  clearHistoryBtn: 'clear-history-btn',
  loadSessionBtn: 'load-session-btn',
  customSessionInput: 'custom-session-input',
  errorContainer: 'error-container',
  warningContainer: 'warning-container',
  serverStatus: 'server-status',
  responseAudio: 'response-audio'
};

// Initialize when page loads
document.addEventListener("DOMContentLoaded", async () => {
  console.log('Enhanced Voice Chat Client initializing...');
  
  // Initialize audio context early
  try {
    await initStreamingAudio();
  } catch (error) {
    console.warn('Audio context will be initialized on first user interaction');
  }
  
  initializeSession();
  setupEventListeners();
  setupErrorHandling();
  checkServerHealth();
  enhanceAccessibility();
  handleOfflineMode();
  setupKeyboardShortcuts();
  
  console.log('Voice Chat Client loaded successfully!');
});

// Event Listeners Setup
function setupEventListeners() {
  console.log('Setting up event listeners...');
  
  // Session management
  const newSessionBtn = getElementById(UI_ELEMENTS.newSessionBtn);
  const clearHistoryBtn = getElementById(UI_ELEMENTS.clearHistoryBtn);
  const loadSessionBtn = getElementById(UI_ELEMENTS.loadSessionBtn);
  
  if (newSessionBtn) newSessionBtn.addEventListener('click', createNewSession);
  if (clearHistoryBtn) clearHistoryBtn.addEventListener('click', clearCurrentSession);
  if (loadSessionBtn) loadSessionBtn.addEventListener('click', loadCustomSession);
  
  // Main record button (unified start/stop)
  const mainRecordButton = getElementById(UI_ELEMENTS.mainRecordButton);
  if (mainRecordButton) {
    mainRecordButton.addEventListener('click', toggleRecording);
    console.log('Record button listener added');
  } else {
    console.error('Main record button not found!');
  }
  
  // Text input and send
  const sendTextButton = getElementById(UI_ELEMENTS.sendTextButton);
  const textInput = getElementById(UI_ELEMENTS.textInput);
  
  if (sendTextButton) sendTextButton.addEventListener('click', sendToAI);
  if (textInput) {
    textInput.addEventListener('keydown', handleTextInputKeydown);
    textInput.addEventListener('input', handleTextInputChange);
  }
  
  // Auto-record toggle
  const autoRecordToggle = getElementById(UI_ELEMENTS.autoRecordToggle);
  if (autoRecordToggle) autoRecordToggle.addEventListener('click', toggleAutoRecord);
  
  // Voice selection
  const voiceSelect = getElementById(UI_ELEMENTS.voiceSelect);
  if (voiceSelect) voiceSelect.addEventListener('change', handleVoiceChange);
  
  console.log('Event listeners setup complete');
}

// Enhanced Recording Toggle
function toggleRecording() {
  console.log('Toggle recording called. Current state:', isRecording, 'Waiting for response:', isWaitingForResponse);
  
  if (isWaitingForResponse) {
    showWarning('Please wait for the current response to complete', 3000);
    return;
  }

  if (!isRecording) {
    startRecording();
  } else {
    stopRecording();
  }
}

// Enhanced Recording Start
async function startRecording() {
  console.log('Starting recording...');
  
  try {
    // Initialize audio context for user interaction
    try {
      await initStreamingAudio();
    } catch (error) {
      console.warn('Audio context initialization deferred:', error);
    }
    
    // Check if browser supports getUserMedia
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Your browser does not support audio recording');
    }

    // Check for microphone permissions first
    const permissions = await navigator.permissions.query({ name: 'microphone' });
    console.log('Microphone permission state:', permissions.state);
    
    if (permissions.state === 'denied') {
      showError('Microphone access denied. Please enable microphone permissions in your browser settings.');
      return;
    }

    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        channelCount: 1,
        sampleRate: 16000
      } 
    });
    
    console.log('Microphone access granted, creating MediaRecorder...');
    
    audioChunks = [];
    
    // Check supported MIME types
    let mimeType = 'audio/webm;codecs=opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = 'audio/webm';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/mp4';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          mimeType = ''; // Let browser choose
        }
      }
    }
    
    console.log('Using MIME type:', mimeType);
    
    const options = mimeType ? { mimeType } : {};
    mediaRecorder = new MediaRecorder(stream, options);
    
    mediaRecorder.ondataavailable = (event) => {
      console.log('Data available:', event.data.size, 'bytes');
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };
    
    mediaRecorder.onstop = async () => {
      console.log('MediaRecorder stopped');
      try {
        recordedBlob = new Blob(audioChunks, { type: mimeType || 'audio/webm' });
        console.log('Recorded blob size:', recordedBlob.size);
        
        if (recordedBlob.size === 0) {
          showError('No audio was recorded. Please try again.');
          return;
        }
        
        const voiceId = getElementById(UI_ELEMENTS.voiceSelect)?.value || 'en-US-natalie';
        await transcribeAndProcess(recordedBlob, voiceId);
        
      } catch (error) {
        console.error('Error processing recording:', error);
        showError('Failed to process recording: ' + error.message);
      } finally {
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => {
          track.stop();
          console.log('Track stopped');
        });
      }
    };
    
    mediaRecorder.onerror = (event) => {
      console.error('MediaRecorder error:', event.error);
      showError('Recording failed: ' + (event.error?.message || 'Unknown error'));
    };
    
    mediaRecorder.start(1000); // Collect data every second
    console.log('MediaRecorder started');
    
    updateRecordingUI(true);
    updateStatus('Recording...', 'recording');
    
    // Add visual feedback
    addRecordingVisualFeedback();
    
  } catch (error) {
    console.error('Failed to start recording:', error);
    handleRecordingError(error);
  }
}

// Enhanced Recording Stop
function stopRecording() {
  console.log('Stopping recording...');
  
  try {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      console.log('MediaRecorder stop() called');
      updateRecordingUI(false);
      updateStatus('Processing recording...', 'processing');
      removeRecordingVisualFeedback();
    } else {
      console.log('MediaRecorder not in recording state:', mediaRecorder?.state);
    }
  } catch (error) {
    console.error('Error stopping recording:', error);
    showError('Failed to stop recording: ' + error.message);
  }
}

// Enhanced UI Update for Recording
function updateRecordingUI(recording) {
  console.log('Updating recording UI:', recording);
  
  const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
  const statusText = getElementById(UI_ELEMENTS.recordStatusText);
  
  isRecording = recording;
  
  if (recordButton) {
    const icon = recordButton.querySelector('.record-icon');
    
    if (recording) {
      recordButton.classList.add('recording');
      if (icon) icon.textContent = '⏹️';
      recordButton.title = 'Click to stop recording';
      recordButton.setAttribute('aria-label', 'Stop recording');
      if (statusText) statusText.textContent = 'Recording... Click to stop';
    } else {
      recordButton.classList.remove('recording', 'processing');
      if (icon) icon.textContent = '🎤';
      recordButton.title = 'Click to start recording';
      recordButton.setAttribute('aria-label', 'Start recording');
      if (statusText) statusText.textContent = 'Click to start recording';
    }
  }
}

// Enhanced Processing UI
function updateProcessingUI(processing) {
  const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
  
  if (recordButton) {
    if (processing) {
      recordButton.classList.add('processing');
      recordButton.disabled = true;
    } else {
      recordButton.classList.remove('processing');
      recordButton.disabled = false;
    }
  }
}

// Fixed transcription function to match backend parameter
async function transcribeAndProcess(audioBlob, voiceId = 'en-US-natalie') {
    console.log('Starting transcription and processing...');
    
    try {
        isWaitingForResponse = true;
        updateProcessingUI(true);
        
        updateStatus('Transcribing and processing...', 'processing');
        
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('voiceId', voiceId);
        
        console.log('Sending request to:', `${SERVER_BASE_URL}/agent/chat/${currentSessionId}`);
        
        const response = await makeRobustAPICall(`${SERVER_BASE_URL}/agent/chat/${currentSessionId}`, {
            method: 'POST',
            body: formData,
            timeout: 60000
        }, false); // Don't parse as JSON, handle streaming
        
        console.log('API Response received, status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        await handleStreamingResponse(response);
        
    } catch (error) {
        console.error('Error in transcribeAndProcess:', error);
        handleProcessingError(error);
    } finally {
        isWaitingForResponse = false;
        updateProcessingUI(false);
    }
}

// Enhanced Text Message Sending with Streaming Support
async function sendToAI() {
  console.log('Sending text message...');
  
  try {
    if (isWaitingForResponse) {
      showWarning('Please wait for the current response to complete', 3000);
      return;
    }

    const textInput = getElementById(UI_ELEMENTS.textInput);
    const text = textInput?.value?.trim();
    
    if (!text) {
      showError('Please enter some text to send', 3000);
      textInput?.focus();
      return;
    }
    
    // Initialize audio context on user interaction
    try {
      await initStreamingAudio();
    } catch (error) {
      console.warn('Audio context initialization deferred:', error);
    }
    
    isWaitingForResponse = true;
    updateProcessingUI(true);
    
    updateStatus('Processing your message...', 'processing');
    
    const voiceId = getElementById(UI_ELEMENTS.voiceSelect)?.value || 'en-US-natalie';
    
    const formData = new FormData();
    formData.append('text', text);
    formData.append('voiceId', voiceId);
    
    console.log('Sending text request to:', `${SERVER_BASE_URL}/agent/chat/${currentSessionId}/text`);
    
    const response = await makeRobustAPICall(`${SERVER_BASE_URL}/agent/chat/${currentSessionId}/text`, {
      method: 'POST',
      body: formData,
      timeout: 60000
    }, false); // Don't parse as JSON, handle streaming
    
    console.log('Text API Response received');
    await handleStreamingResponse(response);
    
    // Clear text input on success
    if (textInput) {
      textInput.value = '';
      handleTextInputChange(); // Update send button state
    }
    
  } catch (error) {
    console.error('Error in sendToAI:', error);
    handleProcessingError(error);
  } finally {
    isWaitingForResponse = false;
    updateProcessingUI(false);
  }
}

// Enhanced API Response Handling (fallback for non-streaming)
async function handleAPIResponse(response) {
  try {
    console.log('Handling API Response:', response);
    
    if (response.error) {
      await handleErrorResponse(response);
      return;
    }
    
    if (response.status === 'success' || response.status === 'success_no_audio') {
      await handleSuccessResponse(response);
    } else {
      showError('Unexpected response format from server');
    }
    
  } catch (error) {
    console.error('Error handling API response:', error);
    showError('Failed to process server response: ' + error.message);
  }
}

// Enhanced Success Response Handling (fallback)
async function handleSuccessResponse(response) {
  console.log('Handling success response...');
  
  // Add messages to chat with animation
  if (response.input) {
    addMessageToChat('user', response.input);
  }
  
  if (response.response) {
    addMessageToChat('assistant', response.response, response.status === 'success_no_audio');
  }
  
  // Play audio if available (non-streaming fallback)
  if (response.audio_urls && response.audio_urls.length > 0) {
    await playResponseAudio(response.audio_urls);
  } else if (response.audio_url) {
    await playResponseAudio([response.audio_url]);
  } else if (response.tts_error) {
    showWarning(response.tts_error_message || 'Audio generation failed, but here\'s the text response', 5000);
  }
  
  // Update session information
  if (response.conversation_turns !== undefined) {
    updateSessionInfo(response.conversation_turns, response.conversation_length);
  }
  
  updateStatus('Response completed!', 'success');
  
  // Auto-record next message if enabled
  if (autoRecordEnabled && !isWaitingForResponse) {
    setTimeout(() => {
      if (!isWaitingForResponse && !isRecording) {
        startRecording();
      }
    }, 1500);
  }
}

// Enhanced Error Response Handling
async function handleErrorResponse(response) {
  console.log('Handling error response:', response);
  
  const errorMessage = response.error_message || 'An unexpected error occurred';
  showError(errorMessage);
  
  if (response.response) {
    addMessageToChat('assistant', response.response, true);
  }
  
  if (response.session_id) {
    await loadSessionHistory();
  }
}

// Enhanced Audio Playback (fallback for non-streaming)
async function playResponseAudio(audioUrls) {
  try {
    console.log('Playing response audio:', audioUrls.length, 'chunks');
    updateStatus('Playing audio response...', 'processing');
    
    const audio = getElementById(UI_ELEMENTS.responseAudio);
    if (!audio) {
      console.error('Audio element not found');
      return;
    }
    
    for (let i = 0; i < audioUrls.length; i++) {
      const audioUrl = audioUrls[i];
      console.log(`Playing audio chunk ${i + 1}/${audioUrls.length}: ${audioUrl}`);
      
      audio.src = audioUrl;
      audio.volume = 0.8;
      
      await new Promise((resolve, reject) => {
        const timeoutId = setTimeout(() => {
          reject(new Error('Audio playback timeout'));
        }, 30000);
        
        const cleanup = () => {
          clearTimeout(timeoutId);
          audio.removeEventListener('ended', onEnded);
          audio.removeEventListener('error', onError);
        };
        
        const onEnded = () => {
          cleanup();
          resolve();
        };
        
        const onError = (error) => {
          cleanup();
          console.error('Audio playback error:', error);
          reject(error);
        };
        
        audio.addEventListener('ended', onEnded, { once: true });
        audio.addEventListener('error', onError, { once: true });
        
        audio.play().catch(reject);
      });
    }
    
    updateStatus('Audio playback completed', 'success');
    
  } catch (error) {
    console.error('Audio playback failed:', error);
    showWarning('Audio playback failed, but you can see the text response above', 5000);
  }
}

// Enhanced Chat Message Addition
function addMessageToChat(role, content, isError = false) {
  const historyContainer = getElementById(UI_ELEMENTS.historyMessages);
  if (!historyContainer) {
    console.error('History container not found');
    return;
  }
  
  console.log('Adding message to chat:', role, content.substring(0, 100) + '...');
  
  // Remove the placeholder if it exists
  const emptyChat = historyContainer.querySelector('.empty-chat');
  if (emptyChat) {
    emptyChat.remove();
  }
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${role} ${isError ? 'error' : ''}`;
  
  const time = new Date().toLocaleTimeString();
  const errorIndicator = isError ? '<span class="error-indicator" title="This message had issues">⚠️</span>' : '';
  
  messageDiv.innerHTML = `
    <div class="message-content">${errorIndicator}${escapeHtml(content)}</div>
    <div class="message-time">${time}</div>
  `;
  
  historyContainer.appendChild(messageDiv);
  
  // Smooth scroll to bottom
  setTimeout(() => {
    historyContainer.scrollTo({
      top: historyContainer.scrollHeight,
      behavior: 'smooth'
    });
  }, 100);
}

// Enhanced Status Update
function updateStatus(message, type = 'info') {
  const statusElement = getElementById(UI_ELEMENTS.statusDisplay);
  if (!statusElement) return;
  
  console.log('Status update:', message, type);
  
  const iconElement = statusElement.querySelector('.status-icon');
  const textElement = statusElement.querySelector('.status-text');
  
  if (textElement) {
    textElement.textContent = message.replace(/^[🟢🔴🟡⚠️🔄🎤⏹️📤🔊✅❌]+ ?/, '');
  }
  
  if (iconElement) {
    const iconMap = {
      'info': '🟢',
      'recording': '🎤',
      'processing': '🔄',
      'success': '✅',
      'error': '❌',
      'warning': '⚠️'
    };
    iconElement.textContent = iconMap[type] || '🟢';
  }
  
  statusElement.className = `status-display ${type}`;
}

// Session Management
function initializeSession() {
  console.log('Initializing session...');
  
  const urlParams = new URLSearchParams(window.location.search);
  const sessionFromUrl = urlParams.get('session');
  
  if (sessionFromUrl && sessionFromUrl.length > 0) {
    currentSessionId = sessionFromUrl;
  } else {
    currentSessionId = generateSessionId();
    updateURL();
  }
  
  const currentSessionElement = getElementById(UI_ELEMENTS.currentSession);
  if (currentSessionElement) {
    currentSessionElement.textContent = currentSessionId;
  }
  
  console.log('Session initialized:', currentSessionId);
  loadSessionHistory();
}

function generateSessionId() {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substr(2, 9);
  return `session-${timestamp}-${random}`;
}

function updateURL() {
  const newUrl = `${window.location.pathname}?session=${currentSessionId}`;
  window.history.replaceState({}, '', newUrl);
}

async function loadSessionHistory() {
  try {
    console.log('Loading session history for:', currentSessionId);
    
    const data = await makeRobustAPICall(`${SERVER_BASE_URL}/agent/history/${currentSessionId}`, {
      timeout: 10000
    });
    
    console.log('Session history loaded:', data);
    
    if (data.status === 'success') {
      updateSessionInfo(data.conversation_turns, data.message_count);
      displayChatHistory(data.history);
    }
  } catch (error) {
    console.error('Failed to load session history:', error);
    showWarning('Could not load conversation history', 5000);
  }
}

function updateSessionInfo(turns, messages) {
  const turnsElement = getElementById(UI_ELEMENTS.conversationTurns);
  const messagesElement = getElementById(UI_ELEMENTS.totalMessages);
  
  if (turnsElement) turnsElement.textContent = turns || 0;
  if (messagesElement) messagesElement.textContent = messages || 0;
}

function displayChatHistory(history) {
  const historyContainer = getElementById(UI_ELEMENTS.historyMessages);
  if (!historyContainer) return;
  
  historyContainer.innerHTML = '';
  
  if (!history || history.length === 0) {
    historyContainer.innerHTML = `
      <div class="empty-chat">
        <div class="empty-icon">💭</div>
        <p>Start a conversation by recording or typing a message</p>
      </div>
    `;
    return;
  }
  
  console.log('Displaying chat history:', history.length, 'messages');
  
  history.forEach((message, index) => {
    setTimeout(() => {
      const messageDiv = document.createElement('div');
      messageDiv.className = `chat-message ${message.role}`;
      
      const time = new Date(message.timestamp * 1000).toLocaleTimeString();
      messageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(message.content)}</div>
        <div class="message-time">${time}</div>
      `;
      
      historyContainer.appendChild(messageDiv);
    }, index * 50); // Staggered animation
  });
  
  setTimeout(() => {
    historyContainer.scrollTop = historyContainer.scrollHeight;
  }, history.length * 50 + 100);
}

function createNewSession() {
  console.log('Creating new session...');
  
  // Stop any ongoing audio
  stopAllAudio();
  
  currentSessionId = generateSessionId();
  const currentSessionElement = getElementById(UI_ELEMENTS.currentSession);
  if (currentSessionElement) {
    currentSessionElement.textContent = currentSessionId;
  }
  
  updateURL();
  
  updateSessionInfo(0, 0);
  const historyContainer = getElementById(UI_ELEMENTS.historyMessages);
  if (historyContainer) {
    historyContainer.innerHTML = `
      <div class="empty-chat">
        <div class="empty-icon">💭</div>
        <p>Start a conversation by recording or typing a message</p>
      </div>
    `;
  }
  updateStatus('New session created!', 'success');
}

async function clearCurrentSession() {
  try {
    console.log('Clearing current session...');
    
    // Stop any ongoing audio
    stopAllAudio();
    
    const response = await makeRobustAPICall(`${SERVER_BASE_URL}/agent/history/${currentSessionId}`, {
      method: 'DELETE',
      timeout: 10000
    });
    
    console.log('Clear session response:', response);
    
    if (response.error) {
      showError(response.error_message || 'Failed to clear session');
      return;
    }
    
    updateSessionInfo(0, 0);
    const historyContainer = getElementById(UI_ELEMENTS.historyMessages);
    if (historyContainer) {
      historyContainer.innerHTML = `
        <div class="empty-chat">
          <div class="empty-icon">💭</div>
          <p>Start a conversation by recording or typing a message</p>
        </div>
      `;
    }
    updateStatus('Session history cleared!', 'success');
    
  } catch (error) {
    console.error('Failed to clear session:', error);
    showError('Failed to clear session history: ' + error.message);
  }
}

function loadCustomSession() {
  const customSessionInput = getElementById(UI_ELEMENTS.customSessionInput);
  const sessionId = customSessionInput?.value?.trim();
  
  if (!sessionId) {
    showError('Please enter a session ID', 3000);
    customSessionInput?.focus();
    return;
  }
  
  // Stop any ongoing audio
  stopAllAudio();
  
  currentSessionId = sessionId;
  const currentSessionElement = getElementById(UI_ELEMENTS.currentSession);
  if (currentSessionElement) {
    currentSessionElement.textContent = currentSessionId;
  }
  
  updateURL();
  
  if (customSessionInput) customSessionInput.value = '';
  loadSessionHistory();
  updateStatus('Session loaded!', 'success');
}

// Enhanced Auto-Record Toggle
function toggleAutoRecord() {
  autoRecordEnabled = !autoRecordEnabled;
  const toggle = getElementById(UI_ELEMENTS.autoRecordToggle);
  const statusElement = toggle?.querySelector('.toggle-status');
  
  if (toggle && statusElement) {
    if (autoRecordEnabled) {
      toggle.classList.add('active');
      statusElement.textContent = 'ON';
    } else {
      toggle.classList.remove('active');
      statusElement.textContent = 'OFF';
    }
  }
  
  updateStatus(`Auto-record ${autoRecordEnabled ? 'enabled' : 'disabled'}`, 'info');
}

// Enhanced Event Handlers
function handleTextInputKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    sendToAI();
  }
}

function handleTextInputChange() {
  const textInput = getElementById(UI_ELEMENTS.textInput);
  const sendButton = getElementById(UI_ELEMENTS.sendTextButton);
  
  if (textInput && sendButton) {
    const hasText = textInput.value.trim().length > 0;
    sendButton.disabled = !hasText || isWaitingForResponse;
    sendButton.style.opacity = hasText && !isWaitingForResponse ? '1' : '0.5';
  }
}

function handleVoiceChange() {
  const voiceSelect = getElementById(UI_ELEMENTS.voiceSelect);
  if (voiceSelect) {
    const selectedVoice = voiceSelect.options[voiceSelect.selectedIndex].text;
    updateStatus(`Voice changed to ${selectedVoice}`, 'info');
  }
}

// Enhanced Error Handling
function handleRecordingError(error) {
  console.error('Recording error:', error);
  
  if (error.name === 'NotAllowedError') {
    showError('Microphone access denied. Please enable microphone permissions and try again.');
  } else if (error.name === 'NotFoundError') {
    showError('No microphone found. Please connect a microphone and try again.');
  } else if (error.name === 'NotReadableError') {
    showError('Microphone is already in use by another application.');
  } else {
    showError('Failed to start recording: ' + error.message);
  }
}

function handleProcessingError(error) {
  console.error('Processing error:', error);
  
  if (error.message.includes('timeout')) {
    showError('The request took too long. Please try with a shorter recording or message.');
  } else if (error.message.includes('No internet') || !navigator.onLine) {
    showError('No internet connection. Please check your network and try again.');
  } else if (error.message.includes('Failed to fetch')) {
    showError('Cannot connect to the server. Please make sure the server is running.');
  } else {
    showError('Failed to process your request: ' + error.message);
  }
}

// Enhanced API Call Function with Streaming Support
async function makeRobustAPICall(url, options = {}, parseJSON = true) {
  console.log('Making API call to:', url);
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options.timeout || 30000);
  
  let attempt = 0;
  const maxAttempts = options.maxRetries || 1;
  
  while (attempt < maxAttempts) {
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          ...options.headers,
        }
      });
      
      clearTimeout(timeoutId);
      
      console.log('API response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      // If we don't want to parse as JSON (for streaming), return the response directly
      if (!parseJSON) {
        return response;
      }
      
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        console.log('API response data:', data);
        return data;
      } else {
        const text = await response.text();
        console.log('API response text:', text.substring(0, 200) + '...');
        return text;
      }
      
    } catch (error) {
      attempt++;
      clearTimeout(timeoutId);
      
      console.error(`API call attempt ${attempt} failed:`, error);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout - the server is taking too long to respond');
      }
      
      if (!navigator.onLine) {
        throw new Error('No internet connection');
      }
      
      if (attempt >= maxAttempts) {
        throw error;
      }
      
      // Wait before retry
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }
}

// Enhanced Notification Functions
function showError(message, duration = 8000) {
  console.error('Showing error:', message);
  updateStatus(`${message}`, 'error');
  
  const errorContainer = getElementById(UI_ELEMENTS.errorContainer);
  if (errorContainer) {
    errorContainer.innerHTML = `
      <div class="error-message">
        <span class="error-icon">⚠️</span>
        <span class="error-text">${escapeHtml(message)}</span>
        <button onclick="hideError()" class="close-btn" title="Dismiss">✖️</button>
      </div>
    `;
    errorContainer.style.display = 'block';
    
    // Auto hide after duration
    setTimeout(hideError, duration);
  }
  
  // Add to browser console for debugging
  console.error('Error:', message);
}

function showWarning(message, duration = 6000) {
  console.warn('Showing warning:', message);
  updateStatus(`${message}`, 'warning');
  
  const warningContainer = getElementById(UI_ELEMENTS.warningContainer);
  if (warningContainer) {
    warningContainer.innerHTML = `
      <div class="warning-message">
        <span class="warning-icon">⚠️</span>
        <span class="warning-text">${escapeHtml(message)}</span>
        <button onclick="hideWarning()" class="close-btn" title="Dismiss">✖️</button>
      </div>
    `;
    warningContainer.style.display = 'block';
    
    // Auto hide after duration
    setTimeout(hideWarning, duration);
  }
  
  console.warn('Warning:', message);
}

function hideError() {
  const errorContainer = getElementById(UI_ELEMENTS.errorContainer);
  if (errorContainer) {
    errorContainer.style.display = 'none';
    errorContainer.innerHTML = '';
  }
}

function hideWarning() {
  const warningContainer = getElementById(UI_ELEMENTS.warningContainer);
  if (warningContainer) {
    warningContainer.style.display = 'none';
    warningContainer.innerHTML = '';
  }
}

// Server Health Check
async function checkServerHealth() {
  try {
    console.log('Checking server health...');
    
    const response = await makeRobustAPICall(`${SERVER_BASE_URL}/health`, {
      method: 'GET',
      timeout: 5000
    });
    
    console.log('Server health response:', response);
    displayHealthStatus(response);
    
    if (response.status === 'degraded') {
      showWarning('Some services are currently unavailable. Functionality may be limited.', 10000);
    }
    
  } catch (error) {
    console.error('Server health check failed:', error);
    displayHealthStatus({ status: 'unhealthy', message: 'Server unavailable' });
    showError('Cannot connect to the server. Please make sure it is running on ' + SERVER_BASE_URL);
  }
}

function displayHealthStatus(health) {
  const statusElement = getElementById(UI_ELEMENTS.serverStatus);
  if (!statusElement) return;
  
  const statusIndicator = statusElement.querySelector('.status-indicator');
  const statusContent = statusElement.querySelector('.server-status-content span');
  
  const statusColors = {
    'healthy': 'var(--success-color, #22c55e)',
    'degraded': 'var(--warning-color, #f59e0b)',
    'unhealthy': 'var(--danger-color, #ef4444)'
  };
  
  if (statusIndicator) {
    statusIndicator.style.background = statusColors[health.status] || statusColors.unhealthy;
    statusIndicator.className = `status-indicator ${health.status}`;
  }
  
  if (statusContent) {
    if (health.apis) {
      statusContent.innerHTML = `
        <div style="font-weight: 700; margin-bottom: 4px;">Server: ${health.status.toUpperCase()}</div>
        <div style="font-size: 0.75rem;">
          STT: ${health.apis.assemblyai?.status || 'Unknown'}<br>
          LLM: ${health.apis.gemini?.status || 'Unknown'}<br>
          TTS: ${health.apis.murf?.status || 'Unknown'}
        </div>
      `;
    } else {
      statusContent.textContent = health.message || `Server: ${health.status}`;
    }
  }
}

// Visual Feedback Functions
function addRecordingVisualFeedback() {
  document.body.classList.add('recording-active');
  
  // Add pulsing effect to record button
  const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
  if (recordButton) {
    recordButton.style.boxShadow = '0 0 30px rgba(239, 68, 68, 0.5)';
  }
}

function removeRecordingVisualFeedback() {
  document.body.classList.remove('recording-active');
  
  const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
  if (recordButton) {
    recordButton.style.boxShadow = '';
  }
}

// Keyboard Shortcuts
function setupKeyboardShortcuts() {
  console.log('Setting up keyboard shortcuts...');
  
  document.addEventListener('keydown', (event) => {
    // Prevent shortcuts when typing in inputs
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
      return;
    }
    
    switch(event.code) {
      case 'Space':
        event.preventDefault();
        toggleRecording();
        break;
        
      case 'Escape':
        event.preventDefault();
        hideError();
        hideWarning();
        if (isRecording) {
          stopRecording();
        }
        // Stop audio playback
        stopAllAudio();
        break;
        
      case 'KeyN':
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          createNewSession();
        }
        break;
        
      case 'KeyC':
        if ((event.ctrlKey || event.metaKey) && event.shiftKey) {
          event.preventDefault();
          clearCurrentSession();
        }
        break;
    }
  });
  
  // Show/hide keyboard hints
  let hintsTimeout;
  document.addEventListener('keydown', () => {
    const hints = document.querySelector('.floating-hints');
    if (hints) {
      hints.style.opacity = '1';
      clearTimeout(hintsTimeout);
      hintsTimeout = setTimeout(() => {
        hints.style.opacity = '0.7';
      }, 3000);
    }
  });
}

// Enhanced Error Handling Setup
function setupErrorHandling() {
  console.log('Setting up error handling...');
  
  // Global error handler
  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showError('An unexpected error occurred. Please refresh the page if problems persist.');
  });

  // Unhandled promise rejection handler
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showError('An unexpected error occurred. Please refresh the page if problems persist.');
    event.preventDefault();
  });

  // Online/offline handlers
  window.addEventListener('online', () => {
    console.log('Connection restored');
    updateStatus('Connection restored', 'success');
    hideError();
    checkServerHealth();
  });

  window.addEventListener('offline', () => {
    console.log('Connection lost');
    showError('No internet connection. Please check your network.');
    updateStatus('No internet connection', 'error');
  });
}

// Accessibility Enhancements
function enhanceAccessibility() {
  console.log('Enhancing accessibility...');
  
  const recordButton = getElementById(UI_ELEMENTS.mainRecordButton);
  const textInput = getElementById(UI_ELEMENTS.textInput);
  
  if (recordButton) {
    recordButton.setAttribute('aria-label', 'Start or stop voice recording');
    recordButton.setAttribute('role', 'button');
    recordButton.setAttribute('tabindex', '0');
  }
  
  if (textInput) {
    textInput.setAttribute('aria-label', 'Type your message here');
  }
  
  // Add focus management
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-navigation');
    }
  });
  
  document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-navigation');
  });
}

// Offline Mode Handling
function handleOfflineMode() {
  if (!navigator.onLine) {
    showError('You are currently offline. Some features may not work.');
  }
  
  // Service worker registration for offline support (if available)
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => {
      console.log('Service worker registration failed:', err);
    });
  }
}

// Utility Functions
function getElementById(id) {
  const element = document.getElementById(id);
  if (!element) {
    console.warn(`Element with ID '${id}' not found`);
  }
  return element;
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Initialize audio context on first user interaction
document.addEventListener('click', async function initAudioOnClick() {
    try {
      await initStreamingAudio();
      console.log('Audio context initialized on user click');
    } catch (error) {
      console.warn('Audio context initialization failed on click:', error);
    }
    document.removeEventListener('click', initAudioOnClick);
}, { once: true });

// Initialize text input change handler with debouncing
document.addEventListener('DOMContentLoaded', () => {
  const textInput = getElementById(UI_ELEMENTS.textInput);
  if (textInput) {
    const debouncedHandler = debounce(handleTextInputChange, 300);
    textInput.addEventListener('input', debouncedHandler);
  }
});

// Periodic health check
setInterval(checkServerHealth, 30000); // Check every 30 seconds

// Export functions for global access (for onclick handlers)
window.hideError = hideError;
window.hideWarning = hideWarning;

// FIXED: Enhanced Debug utilities with better audio diagnostics
window.debugAudio = {
    context: () => audioContext,
    status: () => ({ 
        isPlaying: currentlyPlaying, 
        playbackStarted: playbackStarted,
        bufferQueueLength: audioBufferQueue.length,
        expectedSequence: expectedSequence,
        nextPlayTime: nextPlayTime,
        contextState: audioContext?.state,
        contextTime: audioContext?.currentTime
    }),
    stop: () => stopAllAudio(),
    queue: () => audioBufferQueue,
    test: async () => {
        // Test with a simple beep
        const ctx = await initStreamingAudio();
        if (ctx) {
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);
            
            oscillator.frequency.value = 440; // A4 note
            gainNode.gain.value = 0.1;
            
            oscillator.start();
            oscillator.stop(ctx.currentTime + 0.2);
            
            console.log('Audio test played');
        }
    },
    reset: () => {
        console.log('Resetting audio system');
        stopAllAudio();
        audioBufferQueue = [];
        expectedSequence = 0;
        playbackStarted = false;
        currentlyPlaying = false;
        nextPlayTime = 0;
    },
    simulate: async (text = "This is a test of the audio streaming system") => {
        console.log('Simulating audio stream for text:', text);
        
        // Reset state
        stopAllAudio();
        audioBufferQueue = [];
        expectedSequence = 0;
        playbackStarted = false;
        
        // Send audio config event
        await processStreamEvent({
            type: 'audio_config',
            sample_rate: 24000,
            channels: 1,
            format: 'WAV'
        });
        
        // Simulate chunks
        const words = text.split(' ');
        const chunkSize = 3;
        
        for (let i = 0; i < words.length; i += chunkSize) {
            const chunkWords = words.slice(i, i + chunkSize);
            const isLast = i + chunkSize >= words.length;
            
            // Generate simple WAV data for testing
            const sampleRate = 24000;
            const duration = 0.3; // 300ms
            const samples = Math.floor(sampleRate * duration);
            
            // Create WAV header
            const buffer = new ArrayBuffer(44 + samples * 2);
            const view = new DataView(buffer);
            
            // RIFF header
            const writeString = (offset, string) => {
                for (let i = 0; i < string.length; i++) {
                    view.setUint8(offset + i, string.charCodeAt(i));
                }
            };
            
            writeString(0, 'RIFF');
            view.setUint32(4, 36 + samples * 2, true);
            writeString(8, 'WAVE');
            writeString(12, 'fmt ');
            view.setUint32(16, 16, true);
            view.setUint16(20, 1, true);
            view.setUint16(22, 1, true);
            view.setUint32(24, sampleRate, true);
            view.setUint32(28, sampleRate * 2, true);
            view.setUint16(32, 2, true);
            view.setUint16(34, 16, true);
            writeString(36, 'data');
            view.setUint32(40, samples * 2, true);
            
            // Generate quiet sine wave
            for (let j = 0; j < samples; j++) {
                const sample = Math.sin(2 * Math.PI * 440 * j / sampleRate) * 0.1 * 32767;
                view.setInt16(44 + j * 2, sample, true);
            }
            
            const base64Audio = btoa(String.fromCharCode(...new Uint8Array(buffer)));
            
            await processStreamEvent({
                type: 'audio_chunk',
                audio_data: base64Audio,
                sequence: Math.floor(i / chunkSize),
                duration_ms: 300,
                is_final: isLast
            });
            
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('Audio stream simulation complete');
    }
};

console.log('Enhanced Voice Chat Client with Fixed Seamless Audio Streaming loaded successfully!');
console.log('Available debug commands: window.debugAudio.test(), window.debugAudio.simulate(), window.debugAudio.status(), window.debugAudio.reset()');

// PERFORMANCE MONITORING
let audioMetrics = {
    chunksReceived: 0,
    chunksPlayed: 0,
    totalLatency: 0,
    playbackErrors: 0,
    sequenceErrors: 0
};

// Monitor audio performance
const originalPlayAudioChunk = playAudioChunk;
playAudioChunk = async function(base64Audio, sequence = 0, durationMs = 0) {
    const startTime = performance.now();
    audioMetrics.chunksReceived++;
    
    try {
        const result = await originalPlayAudioChunk(base64Audio, sequence, durationMs);
        
        if (result) {
            audioMetrics.chunksPlayed++;
            audioMetrics.totalLatency += (performance.now() - startTime);
        } else {
            audioMetrics.playbackErrors++;
        }
        
        // Check for sequence errors
        if (sequence !== expectedSequence && audioBufferQueue.length === 0) {
            audioMetrics.sequenceErrors++;
            console.warn(`Sequence error: expected ${expectedSequence}, got ${sequence}`);
        }
        
        return result;
    } catch (error) {
        audioMetrics.playbackErrors++;
        throw error;
    }
};

// Expose metrics
window.debugAudio.metrics = () => ({
    ...audioMetrics,
    averageLatency: audioMetrics.chunksPlayed ? audioMetrics.totalLatency / audioMetrics.chunksPlayed : 0,
    successRate: audioMetrics.chunksReceived ? (audioMetrics.chunksPlayed / audioMetrics.chunksReceived * 100).toFixed(2) + '%' : '0%'
});

// Reset metrics
window.debugAudio.resetMetrics = () => {
    audioMetrics = {
        chunksReceived: 0,
        chunksPlayed: 0,
        totalLatency: 0,
        playbackErrors: 0,
        sequenceErrors: 0
    };
    console.log('Audio metrics reset');
};