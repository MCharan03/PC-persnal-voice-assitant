import sys
import requests
import sounddevice as sd
import numpy as np
import queue
import time
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.wake_word import WakeWord
from modules.vad import VAD
from modules.tts import TTS
from gui import ModernHUD

SERVER_URL = "http://localhost:5001"

class CherryClient(QThread):
    # Updated Signals for ModernHUD
    sig_state = pyqtSignal(str) # "IDLE", "LISTENING", "THINKING", "SPEAKING"
    sig_text = pyqtSignal(str, str) # user_text, ai_text
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.audio_queue = queue.Queue()
        
    def run(self):
        print("--- Initializing Cherry Client ---")
        
        # Local "Reflexes" (Wake Word & VAD need to be local for zero latency)
        self.wake_word = WakeWord(keyword="jarvis")
        self.vad = VAD(threshold=0.02)
        
        # Local Voice Output
        self.tts = TTS()
        
        self.is_listening = False
        self.audio_buffer = []
        self.wake_buffer = []
        
        print(f"Connecting to Brain at {SERVER_URL}...")
        self.sig_state.emit("IDLE")
        
        # Retry Loop for Server Connection
        connected = False
        for i in range(1, 16): # Try 15 times (30 seconds)
            try:
                self.sig_text.emit("System Initializing...", f"Connecting... ({i}/15)")
                requests.get(f"{SERVER_URL}/api/status", timeout=2)
                print("Brain is Online.")
                self.sig_text.emit("System Online", "Ready. Say 'Jarvis'")
                connected = True
                break
            except Exception as e:
                print(f"Waiting for Brain... ({i}/15) - {e}")
                time.sleep(2)
        
        if not connected:
            print(f"WARNING: Brain (Server) appears offline after multiple attempts.")
            self.sig_text.emit("Connection Failed", "Brain is offline.")
            self.tts.speak("I cannot connect to my brain. Please check the server.")

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

        # Calculate volume level
        rms = np.sqrt(np.mean(audio_data**2))
        
        # DEBUG: Print volume level every 10th chunk to verify mic is working
        if np.random.rand() < 0.1:
            print(f"Mic Level: {rms:.4f}")

        if not self.is_listening:
            # Wake Word Detection (Local)
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
            # VAD / Recording
            self.audio_buffer.append(audio_data)
            status = self.vad.process_chunk(audio_data)
            if status == 1: # Silence detected
                self.is_listening = False
                self.sig_state.emit("THINKING")
                
                # Send to Server
                full_audio = np.concatenate(self.audio_buffer)
                self.send_to_brain(full_audio)
                
                # CRITICAL FIX: Flush the audio queue to remove 'stale' audio 
                # recorded while the AI was thinking/speaking.
                with self.audio_queue.mutex:
                    self.audio_queue.queue.clear()
                
                print("--- Cycle Complete. Listening for 'Jarvis' ---")
                self.sig_state.emit("IDLE")

    def send_to_brain(self, audio_data):
        """
        Sends raw audio data to the server for processing.
        """
        import soundfile as sf
        import io
        
        # Convert numpy array to WAV in memory
        mem_file = io.BytesIO()
        sf.write(mem_file, audio_data, 16000, format='WAV')
        mem_file.seek(0)
        
        try:
            print("Sending audio to Brain...")
            files = {'audio': ('command.wav', mem_file, 'audio/wav')}
            response = requests.post(f"{SERVER_URL}/api/voice", files=files)
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('response', '')
                transcription = data.get('transcription', '(Unknown)')
                
                print(f"Brain: {reply}")
                
                self.sig_text.emit(transcription, reply)
                self.sig_state.emit("SPEAKING")
                
                self.tts.speak(reply)
            elif response.status_code == 400:
                print(f"Server (400): {response.text}")
                self.sig_text.emit("...", "I didn't catch that.")
                self.tts.speak("I didn't catch that.")
            else:
                print(f"Server Error ({response.status_code}): {response.text}")
                self.sig_text.emit("Error", "Server Error")
                self.tts.speak("I'm having trouble connecting to my brain.")
                
        except Exception as e:
            print(f"Network Error: {e}")
            self.sig_text.emit("Network Error", str(e))
            self.tts.speak("Network error.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    client = CherryClient()
    
    # Connect signals
    client.sig_state.connect(hud.set_state)
    client.sig_text.connect(hud.set_text)
    
    hud.show()
    client.start()
    sys.exit(app.exec())