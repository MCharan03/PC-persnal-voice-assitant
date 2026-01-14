import sys
import os
import traceback
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from io import BytesIO
import soundfile as sf
import numpy as np

# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.brain_agent import BrainAgent
from modules.stt import STT
from modules.tts import TTS
from modules.bridge import server_bridge
from modules.emotion import EmotionEngine
from modules.pulse import PulseCore

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=10*1024*1024)

print("--- Initializing Server Core ---")

# Link Bridge
server_bridge.set_socket(socketio)

# Initialize Modules
agent = BrainAgent()
ears = STT()
mouth = TTS()
emotion_engine = EmotionEngine()

# Proactive Callback
def pulse_callback(message):
    """Called when Pulse triggers a proactive event."""
    print(f">> [Pulse Event] {message}")
    socketio.emit('response', {'text': message, 'final': True})
    
    # Generate Audio for Proactive Message
    wav_data = mouth.generate_audio_bytes(message)
    if wav_data:
        socketio.emit('audio_output', {'audio': wav_data})

pulse = PulseCore(pulse_callback)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "online", "mode": "Agentic + Emotional"})

# --- PHASE 2: Autonomous Agency Endpoint ---
@app.route('/agent_interact', methods=['POST'])
def agent_interact():
    """
    Direct HTTP endpoint for the Agentic Brain.
    Input: JSON { "message": "Research Flask security" }
    Output: JSON { "response": "..." }
    """
    data = request.json
    user_input = data.get('message')
    
    if not user_input:
        return jsonify({'error': 'No message provided', 'status': 'failed'}), 400

    print(f"[HTTP Agent Request]: {user_input}")
    
    try:
        # 1. Inject Persona & Context (Handled internally by BrainAgent)
        # 2. Run the Agent Loop
        response_text = agent.chat(user_input)
        
        return jsonify({'response': response_text, 'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 500

# --- WebSocket Events (Phase 3: Sensory Perception) ---

@socketio.on('connect')
def handle_connect():
    print('[Socket] Client connected')
    emit('status', {'msg': 'Connected to Cherry Core'})

@socketio.on('audio_input')
def handle_audio(data):
    try:
        audio_bytes = data.get('audio')
        if not audio_bytes: return

        with sf.SoundFile(BytesIO(audio_bytes)) as f:
            audio_data = f.read(dtype='float32')
        
        # 1. Transcribe (Phase 3: Ears)
        user_text = ears.transcribe(audio_data)
        print(f"[User]: {user_text}")
        
        if not user_text:
            emit('response', {'text': "I didn't catch that.", 'final': True})
            return
            
        emit('transcription', {'text': user_text})
        emit('state', {'status': 'thinking'})

        # 2. Analyze Emotion (Phase 4: Emotion)
        mood = emotion_engine.analyze(user_text)
        directive = emotion_engine.get_system_directive(mood)
        print(f"[{mood}] Directive: {directive}")
        
        # 3. Update Agent Mood
        agent.update_mood(directive)

        # 4. Agent Loop (Background)
        socketio.start_background_task(run_agent_task, user_text)
        
    except Exception as e:
        print("Error processing socket audio:")
        traceback.print_exc()
        emit('error', {'msg': str(e)})

def run_agent_task(user_text):
    try:
        response_text = agent.chat(user_text)
        print(f"[Cherry]: {response_text}")
        socketio.emit('response', {'text': response_text, 'final': True})
        
        # Generate Audio
        wav_data = mouth.generate_audio_bytes(response_text)
        if wav_data:
            socketio.emit('audio_output', {'audio': wav_data})
            
    except Exception as e:
        print(f"Agent Task Error: {e}")
        socketio.emit('response', {'text': "I encountered an error thinking about that.", 'final': True})

@socketio.on('screenshot_upload')
def handle_screenshot(data):
    img_data = data.get('image')
    if img_data:
        server_bridge.receive_screenshot(img_data)

if __name__ == '__main__':
    # Using socketio.run instead of app.run for WebSocket support
    socketio.run(app, host='0.0.0.0', port=5001)