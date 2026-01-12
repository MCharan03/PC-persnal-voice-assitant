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

app = Flask(__name__)
# Allow large payloads for audio
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=10*1024*1024)

print("--- Initializing Server Core ---")

agent = BrainAgent()
ears = STT()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "online", "mode": "Agentic"})

# Keep REST API for legacy/testing
@app.route('/api/voice', methods=['POST'])
def voice_command_rest():
    # ... (Same as before, helpful for debugging tools)
    pass

# --- WebSocket Events ---

@socketio.on('connect')
def handle_connect():
    print('[Socket] Client connected')
    emit('status', {'msg': 'Connected to Cherry Core'})

@socketio.on('audio_input')
def handle_audio(data):
    """
    Receives binary audio data (WAV bytes) from client.
    """
    try:
        print(">> [Socket] Received Audio Input")
        audio_bytes = data.get('audio')
        
        if not audio_bytes:
            emit('error', {'msg': 'No audio data'})
            return

        # Convert bytes to numpy via SoundFile
        # Using io.BytesIO to wrap the raw bytes
        with sf.SoundFile(BytesIO(audio_bytes)) as f:
            audio_data = f.read(dtype='float32')
        
        # 1. Transcribe
        user_text = ears.transcribe(audio_data)
        print(f"[User]: {user_text}")
        
        if not user_text:
            emit('response', {'text': "I didn't catch that.", 'final': True})
            return
            
        emit('transcription', {'text': user_text})
        emit('state', {'status': 'thinking'})

        # 2. Agent Loop
        response_text = agent.chat(user_text)
        print(f"[Cherry]: {response_text}")
        
        # Send back result
        emit('response', {'text': response_text, 'final': True})
        
    except Exception as e:
        print("Error processing socket audio:")
        traceback.print_exc()
        emit('error', {'msg': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)
