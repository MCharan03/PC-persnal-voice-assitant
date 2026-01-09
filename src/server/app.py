import sys
import os
import traceback
from flask import Flask, request, jsonify, render_template

# Add the src directory to sys.path to allow importing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.llm import LLM
from modules.actions import Actions
from modules.stt import STT
from flask_socketio import SocketIO, emit
from io import BytesIO
import soundfile as sf

app = Flask(__name__)
# Enable WebSockets
socketio = SocketIO(app, cors_allowed_origins="*")

print("--- Initializing Server Core ---")

# Initialize Core Modules
brain = LLM()
hands = Actions()
ears = STT()

def serialize_llm_response(response):
    """
    Converts internal LLM response (which may contain ToolCall objects) 
    into a JSON-serializable dictionary.
    """
    if isinstance(response, dict) and response.get("type") == "tool":
        return {
            "type": "tool",
            "calls": [
                {
                    "function": {
                        "name": tool.function.name,
                        "arguments": tool.function.arguments
                    }
                }
                for tool in response["calls"]
            ]
        }
    return response

@app.route('/')
def home():
    """Serves the Web Dashboard."""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the health and system stats of the assistant host."""
    try:
        stats = hands.get_system_stats()
        return jsonify({
            "status": "online",
            "system_stats": stats
        })
    except Exception:
        return jsonify({"status": "error", "message": "Health check failed"}), 500

@app.route('/api/voice', methods=['POST'])
def voice_command():
    """
    Accepts an audio file (blob/wav), transcribes it (STT),
    and sends the text to the Brain (LLM).
    """
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
            
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        import time
        start_time = time.time()
        
        # Read file into memory (No Disk I/O)
        audio_bytes = BytesIO(audio_file.read())
        
        # Decode WAV to Numpy Array using SoundFile
        # This ensures Whisper gets exactly what it expects (float32 array)
        data, samplerate = sf.read(audio_bytes)
        data = data.astype('float32')
        
        # 1. Transcribe (Server-side STT)
        t0 = time.time()
        user_text = ears.transcribe(data)
        t1 = time.time()
        print(f"[Timing] STT took: {t1 - t0:.2f}s")
        print(f"[API] Transcribed: {user_text}")
        
        if not user_text:
            return jsonify({"error": "Could not understand audio"}), 400
            
        # 2. Ask Brain
        t2 = time.time()
        response_text = brain.chat(user_text)
        t3 = time.time()
        print(f"[Timing] LLM took: {t3 - t2:.2f}s")
        
        # 3. Execute Actions
        clean_response = ""
        
        if isinstance(response_text, dict) and response_text.get("type") == "tool":
            tool_calls = response_text.get("calls", [])
            for tool in tool_calls:
                result = hands.execute_tool_call(tool.function.name, tool.function.arguments)
                clean_response += str(result) + " "
        else:
            # Legacy Text
            if isinstance(response_text, dict):
                raw = response_text.get("content", "")
            else:
                raw = str(response_text)
            clean_response = hands.parse_and_execute(raw)
        
        total_time = time.time() - start_time
        print(f"[Timing] TOTAL Request time: {total_time:.2f}s")
        
        return jsonify({
            "transcription": user_text,
            "response": clean_response,
            "original_response": serialize_llm_response(response_text)
        })
                
    except Exception as e:
        print("!!! SERVER ERROR !!!")
        traceback.print_exc() # Print full error to console
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    The main endpoint for communicating with the assistant remotely.
    Input: JSON { "text": "Open calculator" }
    Output: JSON { "response": "Opening Calculator...", "command": "[OPEN: calculator]" }
    """
    data = request.json
    user_text = data.get('text', '')
    
    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    print(f"[API] User: {user_text}")
    
    # Ask the Brain
    response_text = brain.chat(user_text)
    
    # Process Actions (Server-side execution)
    clean_response = ""
    if isinstance(response_text, dict) and response_text.get("type") == "tool":
        tool_calls = response_text.get("calls", [])
        for tool in tool_calls:
            result = hands.execute_tool_call(tool.function.name, tool.function.arguments)
            clean_response += str(result) + " "
    else:
        if isinstance(response_text, dict):
            raw = response_text.get("content", "")
        else:
            raw = str(response_text)
        clean_response = hands.parse_and_execute(raw)
    
    return jsonify({
        "original_response": serialize_llm_response(response_text),
        "clean_response": clean_response
    })

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print('[Socket] Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('[Socket] Client disconnected')

if __name__ == '__main__':
    # Run using SocketIO
    # Note: Using port 5001 to avoid ghost conflicts on 5000
    socketio.run(app, host='0.0.0.0', port=5001)
