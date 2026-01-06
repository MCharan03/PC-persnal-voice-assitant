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
from gui import Overlay

SERVER_URL = "http://localhost:5000"

class CherryClient(QThread):
    sig_listening = pyqtSignal()
    sig_processing = pyqtSignal()
    sig_speaking = pyqtSignal()
    sig_idle = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.audio_queue = queue.Queue()
        
    def run(self):
        print("--- Initializing Cherry Client ---")
        
        # Local "Reflexes" (Wake Word & VAD need to be local for zero latency)
        self.wake_word = WakeWord(keyword="cherry")
        self.vad = VAD(threshold=0.02)
        
        # Local Voice Output
        self.tts = TTS()
        
        self.is_listening = False
        self.audio_buffer = []
        self.wake_buffer = []
        
        print(f"Connecting to Brain at {SERVER_URL}...")
        try:
            requests.get(f"{SERVER_URL}/api/status")
            print("Brain is Online.")
        except:
            print("WARNING: Brain (Server) appears offline. Start run_server.bat first!")

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
        if status: print(status, file=sys.stderr)
        self.audio_queue.put(indata.copy().squeeze())

    def process_stream(self, audio_data):
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
                    self.sig_listening.emit()
                    self.tts.speak("Yes?")
        else:
            # VAD / Recording
            self.audio_buffer.append(audio_data)
            status = self.vad.process_chunk(audio_data)
            if status == 1: # Silence detected
                self.is_listening = False
                self.sig_processing.emit()
                
                # Send to Server
                full_audio = np.concatenate(self.audio_buffer)
                self.send_to_brain(full_audio)
                
                self.sig_idle.emit()

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
                print(f"Brain: {reply}")
                
                self.sig_speaking.emit()
                self.tts.speak(reply)
            else:
                print(f"Server Error: {response.text}")
                self.tts.speak("I'm having trouble connecting to my brain.")
                
        except Exception as e:
            print(f"Network Error: {e}")
            self.tts.speak("Network error.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = Overlay()
    client = CherryClient()
    
    client.sig_listening.connect(overlay.show_overlay)
    client.sig_idle.connect(overlay.hide_overlay)
    
    client.start()
    sys.exit(app.exec())
