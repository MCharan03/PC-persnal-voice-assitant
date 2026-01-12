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
from modules.bridge import server_bridge # Import the global bridge

app = Flask(__name__)
# Enable large payloads for audio/images (10MB)
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=10*1024*1024)

print("--- Initializing Server Core ---")

# Link Bridge to Socket
server_bridge.set_socket(socketio)

agent = BrainAgent()
ears = STT()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "online", "mode": "Agentic"})

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
        # print(">> [Socket] Received Audio Input")
        audio_bytes = data.get('audio')
        
        if not audio_bytes:
            emit('error', {'msg': 'No audio data'})
            return

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
        # The agent might call tools. If it calls 'see_screen', 
        # the tool will block here waiting for the bridge.
        # Ideally, we should run this in a background thread to not block the socket listener?
        # Flask-SocketIO with eventlet/gevent handles concurrency, so this *should* be okay 
        # provided we don't block the *event loop* entirely. 
        # However, since 'agent.chat' is synchronous, it blocks this event handler.
        # If the tool waits for a message from the SAME client, and the client cannot send 
        # because the server is blocked processing the previous message... DEADLOCK.
        
        # FIX: Run agent chat in a background thread!
        socketio.start_background_task(run_agent_task, user_text)
        
    except Exception as e:
        print("Error processing socket audio:")
        traceback.print_exc()
        emit('error', {'msg': str(e)})

def run_agent_task(user_text):
    """Background task to run the agent so we don't block the socket loop."""
    try:
        response_text = agent.chat(user_text)
        print(f"[Cherry]: {response_text}")
        socketio.emit('response', {'text': response_text, 'final': True})
    except Exception as e:
        print(f"Agent Task Error: {e}")
        socketio.emit('response', {'text': "I encountered an error thinking about that.", 'final': True})

@socketio.on('screenshot_upload')
def handle_screenshot(data):
    print(">> [Socket] Received Screenshot")
    img_data = data.get('image') # Expecting base64 string or bytes
    if img_data:
        server_bridge.receive_screenshot(img_data)

if __name__ == '__main__':
    # Using allow_unsafe_werkzeug to avoid issues during dev if needed, 
    # but socketio.run usually handles it.
    socketio.run(app, host='0.0.0.0', port=5001)