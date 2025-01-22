document.addEventListener('DOMContentLoaded', function() {
    const videoElement = document.getElementById('videoElement');
    const startRecordingButton = document.getElementById('startRecording');
    const stopRecordingButton = document.getElementById('stopRecording');
    const audioOutput = document.getElementById('audioOutput');

    // Initialize Wavesurfer
    var wavesurfer = WaveSurfer.create({
        container: '#waveform',
        waveColor: 'violet',
        progressColor: 'purple',
        barWidth: 2
    });

    videoElement.muted = true;

    let mediaRecorder;
    let recordedBlobs;

    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
            videoElement.srcObject = stream;
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
            recordedBlobs = [];
            mediaRecorder.ondataavailable = event => {
                if (event.data && event.data.size > 0) {
                    recordedBlobs.push(event.data);
                }
            };
        })
        .catch(error => console.error('getUserMedia error:', error));

    startRecordingButton.onclick = () => {
        mediaRecorder.start(10);
        startRecordingButton.disabled = true;
        stopRecordingButton.disabled = false;
    };

    stopRecordingButton.onclick = () => {
        mediaRecorder.stop();
        startRecordingButton.disabled = false;
        stopRecordingButton.disabled = true;
        
        const videoBlob = new Blob(recordedBlobs, { type: 'video/webm' });
        const formData = new FormData();
        formData.append('video', videoBlob);
        
        fetch('/upload', {
            method: 'POST',
            body: formData,
        }).then(response => response.json())
          .then(data => {
                // Load the audio URL into Wavesurfer
                wavesurfer.load(`${data.audioUrl}?t=${new Date().getTime()}`);
          }).catch(error => console.error('Error uploading:', error));
    };

    // Wavesurfer events
    wavesurfer.on('ready', function() {
        // Display the audio player
        audioOutput.style.display = 'block';  // Make the audio element visible
        wavesurfer.play();
    });
});
