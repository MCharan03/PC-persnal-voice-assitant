const socket = io();
const statusEl = document.getElementById('status-text');
const outputDiv = document.getElementById('output-area');
const micBtn = document.getElementById('mic-trigger');
const canvas = document.getElementById('audio-vis');
const ctx = canvas.getContext('2d');

// --- Audio Visualization State ---
let audioCtx;
let analyser;
let dataArray;
let source;
let isVisualizing = false;
let animationId;

// --- Initialize Visualizer ---
function initAudio() {
    if (audioCtx) return;
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256; // Controls bar count
    const bufferLength = analyser.frequencyBinCount;
    dataArray = new Uint8Array(bufferLength);
}

// --- Draw Loop (Iron Man Arc Reactor Style) ---
function draw() {
    if (!isVisualizing) return;
    animationId = requestAnimationFrame(draw);
    
    analyser.getByteFrequencyData(dataArray);
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 50; // Inner circle
    
    // Draw Inner Circle (Core)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius - 10, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(0, 255, 255, 0.1)';
    ctx.fill();
    ctx.strokeStyle = '#00ffff';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw Frequency Bars (Radial)
    const bars = 40;
    const step = (Math.PI * 2) / bars;
    
    for (let i = 0; i < bars; i++) {
        const value = dataArray[i] || 0;
        const barHeight = (value / 255) * 60; // Max height
        
        const angle = i * step;
        
        // Start point (on circle)
        const x1 = centerX + Math.cos(angle) * radius;
        const y1 = centerY + Math.sin(angle) * radius;
        
        // End point (outward)
        const x2 = centerX + Math.cos(angle) * (radius + barHeight);
        const y2 = centerY + Math.sin(angle) * (radius + barHeight);
        
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = `rgba(0, 255, 255, ${value/255})`;
        ctx.lineWidth = 4;
        ctx.stroke();
    }
}

// --- Socket Events ---
socket.on('connect', () => {
    statusEl.innerText = "SYSTEM ONLINE";
    statusEl.classList.remove('blink');
    addMessage("Connection established. Neural link active.", "cherry");
});

socket.on('disconnect', () => {
    statusEl.innerText = "OFFLINE";
    statusEl.classList.add('blink');
});

socket.on('state', (data) => {
    statusEl.innerText = data.status.toUpperCase();
});

socket.on('transcription', (data) => {
    addMessage(data.text, 'user');
});

socket.on('response', (data) => {
    // Phase 4: Streaming Text Effect
    typeWriter(data.text, 'cherry');
});

socket.on('audio_output', (data) => {
    // Play received TTS audio
    if (!audioCtx) initAudio();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    
    // Connect Visualizer
    isVisualizing = true;
    draw();

    // Decode and Play
    audioCtx.decodeAudioData(data.audio, (buffer) => {
        const source = audioCtx.createBufferSource();
        source.buffer = buffer;
        source.connect(analyser); // Connect to visualizer
        analyser.connect(audioCtx.destination); // Connect to speakers
        
        source.onended = () => {
            isVisualizing = false;
            cancelAnimationFrame(animationId);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        };
        
        source.start(0);
    });
});

// --- UI Logic ---
function addMessage(text, type) {
    // Clean old messages to keep display clean?
    // For now, just append.
    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.innerText = text;
    outputDiv.appendChild(div);
    
    // Auto-scroll
    const container = document.querySelector('.hud-container');
    // outputDiv is flex-end, so it stays at bottom usually, 
    // but if it overflows the HUD container we need scroll.
    // Ideally we want only latest messages.
}

function typeWriter(text, type) {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    outputDiv.appendChild(div);
    
    let i = 0;
    const speed = 20; // ms per char
    
    function type() {
        if (i < text.length) {
            div.innerText += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// --- Microphone Handling ---
let mediaRecorder;
let chunks = [];

micBtn.addEventListener('mousedown', async () => {
    if (!audioCtx) initAudio();
    if (audioCtx.state === 'suspended') await audioCtx.resume();
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // 1. Connect to Visualizer
        source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyser);
        isVisualizing = true;
        draw();
        
        // 2. Start Recording
        mediaRecorder = new MediaRecorder(stream);
        chunks = [];
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/wav' });
            
            // Convert Blob to ArrayBuffer to send via SocketIO
            // (SocketIO handles binary automatically usually, but let's be safe)
            // Actually, app.py expects 'audio' key with bytes.
            const reader = new FileReader();
            reader.readAsArrayBuffer(blob);
            reader.onloadend = () => {
                 socket.emit('audio_input', { audio: reader.result });
            };
            
            // Stop Visualizer
            isVisualizing = false;
            cancelAnimationFrame(animationId);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Stop Stream tracks
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        micBtn.classList.add('active');
        statusEl.innerText = "LISTENING";
        
    } catch (err) {
        console.error(err);
        addMessage("Mic Error: " + err.message, "cherry");
    }
});

micBtn.addEventListener('mouseup', () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        micBtn.classList.remove('active');
        statusEl.innerText = "PROCESSING";
    }
});
