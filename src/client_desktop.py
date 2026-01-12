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
from PyQt6.QtCore import QThread, pyqtSignal, QTimer

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
        self.wake_word = WakeWord(keyword="jarvis")
        self.vad = VAD(threshold=0.02)
        self.tts = TTS()
        
        # State Management
        self.state = "IDLE" # IDLE, ACTIVE (Listening), THINKING, SPEAKING, FOLLOWUP
        self.audio_buffer = []
        self.wake_buffer = []
        
        # Continuous Listen Timer
        self.followup_end_time = 0
        
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
            
            self.set_state("SPEAKING")
            self.tts.speak(text)
            
            # After speaking, enter Follow-up Mode for 8 seconds
            # Note: TTS is non-blocking in 'speak', but blocks in '_run_worker'.
            # We rely on is_busy() to know when it finishes.

        @self.sio.event
        def request_screenshot():
            print(">> [Socket] Brain requested screenshot.")
            self.sig_text.emit("...", "Analyzing screen...")
            img_b64 = self.vision.capture_screen()
            self.sio.emit('screenshot_upload', {'image': img_b64})

    def set_state(self, new_state):
        self.state = new_state
        self.sig_state.emit(new_state)

    def run(self):
        print("--- Initializing Cherry Client ---")
        self.set_state("IDLE")
        
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

        with sd.InputStream(samplerate=16000, blocksize=1024, channels=1, callback=self.audio_callback):
            while self.running:
                try:
                    audio_data = self.audio_queue.get(timeout=0.1)
                    self.process_stream(audio_data)
                except queue.Empty:
                    # Check TTS Status to transition from SPEAKING -> FOLLOWUP
                    if self.state == "SPEAKING" and not self.tts.is_busy():
                        print(">> TTS Finished. Entering Follow-up Mode.")
                        self.set_state("FOLLOWUP")
                        self.followup_end_time = time.time() + 8.0 # 8 seconds window
                        self.sig_text.emit("...", "Listening for follow-up...")
                    
                    # Check Follow-up Timeout
                    if self.state == "FOLLOWUP" and time.time() > self.followup_end_time:
                        print(">> Follow-up timeout. Returning to IDLE.")
                        self.set_state("IDLE")
                        self.sig_text.emit("...", "Say 'Jarvis'")
                    
                    continue

    def audio_callback(self, indata, frames, time, status):
        if status: print(f"Audio Error: {status}", file=sys.stderr)
        self.audio_queue.put(indata.copy().squeeze())

    def process_stream(self, audio_data):
        # 1. ALWAYS Listen for Wake Word (Barge-In)
        # We assume Wake Word engine is fast enough to run on every chunk
        self.wake_buffer.append(audio_data)
        if len(self.wake_buffer) > 24: self.wake_buffer.pop(0)
        
        if len(self.wake_buffer) % 8 == 0:
            combined = np.concatenate(self.wake_buffer)
            if self.wake_word.detect(combined):
                print(">> INTERRUPTION / WAKE WORD DETECTED <<")
                
                if self.state == "SPEAKING":
                    self.tts.stop() # Kill TTS
                
                self.set_state("ACTIVE")
                self.audio_buffer = []
                self.wake_buffer = []
                self.sig_text.emit("Listening...", "")
                self.tts.play_listening_cue()
                return

        # 2. State-Based Logic
        if self.state == "IDLE":
            pass # Waiting for Wake Word (handled above)
            
        elif self.state == "FOLLOWUP":
            # In Follow-up, we treat any speech as a command (no wake word needed)
            # Use VAD to detect start of speech
            vad_status = self.vad.process_chunk(audio_data)
            if vad_status == 0: # Speech detected (VAD returns 0 for speech usually? Wait, VAD returns 1 for silence usually in our code?)
                # Let's check VAD implementation logic. 
                # Assuming VAD.process_chunk returns 1 for SILENCE_DETECTED (end of speech) or similar.
                # Actually, standard VAD: 
                # If we detect speech energy, transition to ACTIVE.
                # For simplicity, let's treat FOLLOWUP same as ACTIVE but with timeout.
                
                # Check RMS/Energy to detect start of speech
                if np.sqrt(np.mean(audio_data**2)) > 0.01: # Simple threshold
                    self.set_state("ACTIVE")
                    self.audio_buffer = []
        
        elif self.state == "ACTIVE":
            # Recording Command
            self.audio_buffer.append(audio_data)
            status = self.vad.process_chunk(audio_data)
            
            if status == 1: # Silence detected (End of phrase)
                print(">> Phrase Complete. Sending to Brain.")
                self.set_state("THINKING")
                
                full_audio = np.concatenate(self.audio_buffer)
                self.send_to_brain(full_audio)
                self.audio_buffer = [] # Clear buffer

    def send_to_brain(self, audio_data):
        try:
            mem_file = io.BytesIO()
            sf.write(mem_file, audio_data, 16000, format='WAV')
            wav_bytes = mem_file.getvalue()
            self.sio.emit('audio_input', {'audio': wav_bytes})
        except Exception as e:
            print(f"Socket Error: {e}")
            self.sig_text.emit("Network Error", str(e))
            self.set_state("IDLE")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    client = CherryClient()
    
    client.sig_state.connect(hud.set_state)
    client.sig_text.connect(hud.set_text)
    
    hud.show()
    client.start()
    sys.exit(app.exec())
