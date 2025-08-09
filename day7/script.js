// document.addEventListener("DOMContentLoaded", () => {
//   // Interaction button logic (optional)
//   const interactionBtn = document.getElementById("interaction-btn");
//   const interactionMsg = document.getElementById("interaction-message");

//   if (interactionBtn && interactionMsg) {
//     interactionBtn.addEventListener("click", () => {
//       interactionMsg.textContent =
//         "You just clicked the button! More to come soon...";
//     });
//   }

//   // Voice generation logic
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
// });
// //ECHO BOT logic
// let mediaRecorder;
// let audioChunks = [];
// let recordedBlob;

// // Buttons
// const startBtn = document.getElementById("start-recording");
// const stopBtn = document.getElementById("stop-recording");
// const uploadBtn = document.getElementById("upload-audio");
// const audioPlayer = document.getElementById("recorded-audio");
// const statusMsg = document.getElementById("upload-status");

// startBtn.addEventListener("click", async () => {
//   const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

//   mediaRecorder = new MediaRecorder(stream);
//   audioChunks = [];

//   mediaRecorder.ondataavailable = (event) => {
//     audioChunks.push(event.data);
//   };

//   mediaRecorder.onstop = () => {
//     recordedBlob = new Blob(audioChunks, { type: "audio/webm" });
//     const audioUrl = URL.createObjectURL(recordedBlob);
//     audioPlayer.src = audioUrl;
//     audioPlayer.play();
//   };

//   mediaRecorder.start();
//   startBtn.disabled = true;
//   stopBtn.disabled = false;
// });

// stopBtn.addEventListener("click", () => {
//   if (mediaRecorder && mediaRecorder.state !== "inactive") {
//     mediaRecorder.stop();
//     startBtn.disabled = false;
//     stopBtn.disabled = true;
//     echoMurfBtn.disabled = false; 
//   }
// });

// uploadBtn.addEventListener("click", async () => {
//   if (!recordedBlob) return alert("Please record something first!");

//   const formData = new FormData();
//   formData.append("file", recordedBlob, "recording.webm");

//   statusMsg.textContent = "Uploading...";

//   try {
//     const res = await fetch("http://127.0.0.1:8000/upload-audio/", {
//       method: "POST",
//       body: formData,
//     });

//     const data = await res.json();
//     statusMsg.textContent = `✅ Uploaded: ${data.filename} (${data.content_type}), ${data.size} bytes`;
//     //Transcribing
//      transcribeAudio(recordedBlob);
//   } catch (err) {
//     console.error(err);
//     statusMsg.textContent = "❌ Upload failed!";
//   }
// });


// //Transcribe logic

// async function transcribeAudio(blob) {
//     const formData = new FormData();
//     formData.append("file", blob, "recording.wav");

//     const statusDiv = document.getElementById("status");
//     const transcriptDiv = document.getElementById("transcript");

//     statusDiv.innerText = "Transcribing...";

//     try {
//         const response = await fetch("http://localhost:8000/transcribe/file", {
//             method: "POST",
//             body: formData,
//         });

//         if (!response.ok) {
//             throw new Error("Transcription failed.");
//         }

//         const data = await response.json();
//         statusDiv.innerText = "Transcription complete!";
//         transcriptDiv.innerText = data.transcript;
//     } catch (err) {
//         console.error(err);
//         statusDiv.innerText = "Transcription error.";
//         transcriptDiv.innerText = "";
//     }
// }

// // DAY7
// document.addEventListener("DOMContentLoaded", function () {
//     const echoMurfBtn = document.getElementById("echoMurfBtn");
//     const voiceSelect = document.getElementById("voiceSelect");
//     const echoAudio = document.getElementById("echoAudio");

//     let recordedBlob = null;

//     // Example: capturing your recording from elsewhere in your code
//     // recordedBlob should be set after stopRecording
//     window.setRecordedBlob = function(blob) {
//         recordedBlob = blob;
//     };

//     echoMurfBtn.addEventListener("click", async () => {
//         if (!recordedBlob) {
//             alert("Please record something first!");
//             return;
//         }

//         const formData = new FormData();
//         formData.append("audio_file", recordedBlob, "recording.webm");
//         formData.append("voiceId", voiceSelect.value);

//         try {
//             const res = await fetch("/tts/echo", {
//                 method: "POST",
//                 body: formData
//             });

//             const result = await res.json();

//             if (result.error) {
//                 console.error(result.error);
//                 alert(result.error);
//                 return;
//             }

//             console.log("Echo transcription:", result.text);
//             echoAudio.src = result.audio_url;
//             echoAudio.play();

//         } catch (err) {
//             console.error("Error calling /tts/echo:", err);
//             alert("Something went wrong.");
//         }
//     });
// });


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