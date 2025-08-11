document.addEventListener("DOMContentLoaded", () => {
  // Interaction button logic (optional)
  const interactionBtn = document.getElementById("interaction-btn");
  const interactionMsg = document.getElementById("interaction-message");

  if (interactionBtn && interactionMsg) {
    interactionBtn.addEventListener("click", () => {
      interactionMsg.textContent =
        "You just clicked the button! More to come soon...";
    });
  }

  // Voice generation logic
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
});

//ECHO BOT logic
let mediaRecorder;
let audioChunks = [];
let recordedBlob;

// Buttons
const startBtn = document.getElementById("start-recording");
const stopBtn = document.getElementById("stop-recording");
const uploadBtn = document.getElementById("upload-audio");
const audioPlayer = document.getElementById("recorded-audio");
const statusMsg = document.getElementById("upload-status");

startBtn.addEventListener("click", async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = () => {
    recordedBlob = new Blob(audioChunks, { type: "audio/webm" });
    const audioUrl = URL.createObjectURL(recordedBlob);
    audioPlayer.src = audioUrl;
    audioPlayer.play();
  };

  mediaRecorder.start();
  startBtn.disabled = true;
  stopBtn.disabled = false;
});

stopBtn.addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
    // FIXED: Enable echo button after stopping
    document.getElementById("echo-murf").disabled = false;
     // NEW: Enable LLM button after stopping
    document.getElementById("llm-chat").disabled = false;
  }
});

uploadBtn.addEventListener("click", async () => {
  if (!recordedBlob) return alert("Please record something first!");

  const formData = new FormData();
  formData.append("file", recordedBlob, "recording.webm");

  statusMsg.textContent = "Uploading...";

  try {
    const res = await fetch("http://127.0.0.1:8000/upload-audio/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    statusMsg.textContent = `✅ Uploaded: ${data.filename} (${data.content_type}), ${data.size} bytes`;
    //Transcribing
     transcribeAudio(recordedBlob);
  } catch (err) {
    console.error(err);
    statusMsg.textContent = "❌ Upload failed!";
  }
});


//Transcribe logic
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

// FIXED Echo Bot v2 functionality
document.getElementById("echo-murf").addEventListener("click", async () => {
    if (!recordedBlob) {
        alert("Please record something first!");
        return;
    }

    const formData = new FormData();
    formData.append("audio_file", recordedBlob, "recording.webm");
    
    // Add voice selection if select exists
    const voiceSelect = document.getElementById("voiceSelect");
    if (voiceSelect) {
        formData.append("voiceId", voiceSelect.value);
    }

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
        
        // Play the Murf audio
        audioPlayer.src = result.audio_url;
        audioPlayer.play();

    } catch (err) {
        console.error("Error:", err);
        alert("Echo processing failed.");
        statusMsg.textContent = "❌ Echo failed!";
    }
});

// NEW: LLM Chat functionality - ADD THIS TO THE END OF YOUR FILE
document.getElementById("llm-chat").addEventListener("click", async () => {
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

    statusMsg.textContent = "🤖 Processing with LLM...";
    
    // Update UI to show LLM processing
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

        // Display results
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
        
        // Play the LLM response audio
        if (result.audio_url) {
            audioPlayer.src = result.audio_url;
            audioPlayer.play();
            
            // If multiple chunks, play them sequentially
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
});

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