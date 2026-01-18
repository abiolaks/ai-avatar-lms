const recordButton = document.getElementById('recordButton');
const statusDiv = document.getElementById('status');
const conversationLog = document.getElementById('conversationLog');
const avatarFace = document.querySelector('.avatar-face');
const recommendationPanel = document.getElementById('recommendation-panel');
const courseDetails = document.getElementById('course-details');

let ws;
let mediaRecorder;
let audioChunks = [];

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/avatar`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        statusDiv.textContent = 'Connected';
        statusDiv.className = 'status connected';
    };

    ws.onclose = () => {
        statusDiv.textContent = 'Disconnected';
        statusDiv.className = 'status disconnected';
        setTimeout(connectWebSocket, 3000); // Reconnect
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleServerMessage(data);
    };
}

function handleServerMessage(data) {
    if (data.type === 'transcript') {
        addMessage(data.text, 'user');
    } else if (data.type === 'response_text') {
        addMessage(data.text, 'ai');

        if (data.audio_url) {
            playAudio(data.audio_url);
        } else {
            speakVisuals(data.text); // Fallback
        }

        if (data.action === 'recommend_course' && data.data) {
            showRecommendation(data.data);
        }
    }
}

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.textContent = text;
    conversationLog.appendChild(div);
    conversationLog.scrollTop = conversationLog.scrollHeight;
}

function playAudio(url) {
    const audio = new Audio(url);
    avatarFace.classList.add('speaking');
    audio.onended = () => {
        avatarFace.classList.remove('speaking');
    };
    audio.play().catch(e => console.error("Audio play failed", e));
}

function speakVisuals(text) {
    // Simple visual simulation of speaking (fallback)
    const duration = Math.min(text.length * 50, 3000);
    avatarFace.classList.add('speaking');
    setTimeout(() => {
        avatarFace.classList.remove('speaking');
    }, duration);
}

function showRecommendation(data) {
    if (!data.recommendations || data.recommendations.length === 0) return;

    const course = data.recommendations[0];
    const html = `
        <div class="course-card">
            <div class="course-title">${course.title}</div>
            <div class="course-meta">Match: ${course.match_score}% | ${course.difficulty} | ${course.duration_hours}h</div>
            <div class="course-desc">${course.description}</div>
            <button class="btn-enroll" onclick="window.open('${course.action_url}', '_blank')">Enroll Now</button>
        </div>
    `;
    courseDetails.innerHTML = html;
    recommendationPanel.classList.remove('hidden');
}

// Audio Recording Logic
recordButton.addEventListener('mousedown', startRecording);
recordButton.addEventListener('mouseup', stopRecording);
recordButton.addEventListener('touchstart', startRecording); // Mobile support
recordButton.addEventListener('touchend', stopRecording);

async function startRecording(e) {
    e.preventDefault();
    if (ws.readyState !== WebSocket.OPEN) return;

    statusDiv.textContent = 'Recording...';
    statusDiv.className = 'status recording';
    audioChunks = [];

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            sendAudio(audioBlob);
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
    } catch (err) {
        console.error('Error accessing microphone:', err);
        addMessage('Error accessing microphone', 'system');
    }
}

function stopRecording(e) {
    e.preventDefault();
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        statusDiv.textContent = 'Processing...';
        statusDiv.className = 'status connected'; // Reset status
    }
}

function sendAudio(blob) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(blob);
    }
}

// Init
connectWebSocket();
