import sys
import os
import io
import queue
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import socketio
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.wake_word import WakeWord
from modules.vad import VAD
from modules.tts import TTS
from modules.vision import Vision
from gui import ModernHUD

SERVER_URL = "http://localhost:5001"

class CherryClient(QThread):
    sig_state = pyqtSignal(str) # "IDLE", "LISTENING", "THINKING", "SPEAKING"
    sig_text = pyqtSignal(str, str) # user_text, ai_text
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.audio_queue = queue.Queue()
        
        # Modules
        self.vision = Vision()
        
        # SocketIO Client
        self.sio = socketio.Client()
        self.setup_socket_events()

    def setup_socket_events(self):
        @self.sio.event
        def connect():
            print("[Socket] Connected to Brain!")
            self.sig_text.emit("System Online", "Ready. Say 'Jarvis'")
            
        @self.sio.event
        def disconnect():
            print("[Socket] Disconnected from Brain!")
            self.sig_text.emit("Connection Lost", "Brain offline.")
            
        @self.sio.event
        def transcription(data):
            text = data.get('text', '')
            self.sig_text.emit(text, "...")
            
        @self.sio.event
        def response(data):
            text = data.get('text', '')
            print(f"Brain: {text}")
            self.sig_text.emit("...", text)
            self.sig_state.emit("SPEAKING")
            self.tts.speak(text)
            self.sig_state.emit("IDLE")

        @self.sio.event
        def request_screenshot():
            print(">> [Socket] Brain requested screenshot.")
            self.sig_text.emit("...", "Analyzing screen...")
            
            # Capture
            img_b64 = self.vision.capture_screen()
            
            if img_b64:
                print(f">> Sending screenshot ({len(img_b64)} bytes)...")
                self.sio.emit('screenshot_upload', {'image': img_b64})
            else:
                print(">> Screenshot failed.")
                self.sio.emit('screenshot_upload', {'image': None})

    def run(self):
        print("--- Initializing Cherry Client ---")
        
        self.wake_word = WakeWord(keyword="jarvis")
        self.vad = VAD(threshold=0.02)
        self.tts = TTS()
        
        self.is_listening = False
        self.audio_buffer = []
        self.wake_buffer = []
        
        self.sig_state.emit("IDLE")
        
        # Connect to Server
        connected = False
        for i in range(1, 16):
            try:
                self.sig_text.emit("System Initializing...", f"Connecting... ({i}/15)")
                self.sio.connect(SERVER_URL)
                connected = True
                break
            except Exception as e:
                print(f"Connection Failed: {e}")
                time.sleep(2)
                
        if not connected:
            self.sig_text.emit("Connection Failed", "Brain is offline.")
            self.tts.speak("I cannot connect to my brain.")

        device_info = sd.query_devices(kind='input')
        print(f"Using Input Device: {device_info['name']}")

        with sd.InputStream(samplerate=16000, blocksize=1024, channels=1, callback=self.audio_callback):
            while self.running:
                try:
                    audio_data = self.audio_queue.get(timeout=1)
                    self.process_stream(audio_data)
                except queue.Empty:
                    continue

    def audio_callback(self, indata, frames, time, status):
        if status: 
            print(f"Audio Error: {status}", file=sys.stderr)
        self.audio_queue.put(indata.copy().squeeze())

    def process_stream(self, audio_data):
        # Prevent hearing itself
        if self.tts.is_busy():
            self.wake_buffer = []
            self.audio_buffer = []
            return

        if not self.is_listening:
            # Wake Word Detection
            self.wake_buffer.append(audio_data)
            if len(self.wake_buffer) > 24: self.wake_buffer.pop(0)
            
            if len(self.wake_buffer) % 8 == 0:
                combined = np.concatenate(self.wake_buffer)
                if self.wake_word.detect(combined):
                    print("Wake Word Detected!")
                    self.is_listening = True
                    self.audio_buffer = []
                    self.wake_buffer = []
                    
                    self.sig_state.emit("LISTENING")
                    self.sig_text.emit("Listening...", "")
                    self.tts.speak("Yes?")
        else:
            # VAD
            self.audio_buffer.append(audio_data)
            status = self.vad.process_chunk(audio_data)
            
            if status == 1: # Silence detected
                self.is_listening = False
                self.sig_state.emit("THINKING")
                
                # Send to Server via Socket
                full_audio = np.concatenate(self.audio_buffer)
                self.send_to_brain(full_audio)
                
                # Clear queue
                with self.audio_queue.mutex:
                    self.audio_queue.queue.clear()

    def send_to_brain(self, audio_data):
        """
        Sends raw audio data to the server via SocketIO.
        """
        try:
            # Convert numpy array to WAV in memory
            mem_file = io.BytesIO()
            sf.write(mem_file, audio_data, 16000, format='WAV')
            wav_bytes = mem_file.getvalue()
            
            self.sio.emit('audio_input', {'audio': wav_bytes})
            # print(">> Sent audio to Brain")
            
        except Exception as e:
            print(f"Socket Error: {e}")
            self.sig_text.emit("Network Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    client = CherryClient()
    
    client.sig_state.connect(hud.set_state)
    client.sig_text.connect(hud.set_text)
    
    hud.show()
    client.start()
    sys.exit(app.exec())