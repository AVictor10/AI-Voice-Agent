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

const startBtn = document.getElementById("start-recording");
const stopBtn = document.getElementById("stop-recording");
const audioPlayer = document.getElementById("recorded-audio");

startBtn.addEventListener("click", async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    const audioUrl = URL.createObjectURL(audioBlob);
    audioPlayer.src = audioUrl;
    audioPlayer.play();
  };

  mediaRecorder.start();
  startBtn.disabled = true;
  stopBtn.disabled = false;
});

stopBtn.addEventListener("click", () => {
  mediaRecorder.stop();
  startBtn.disabled = false;
  stopBtn.disabled = true;
});


