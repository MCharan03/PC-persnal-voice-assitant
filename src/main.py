import sys
import time
import queue
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QObject

# Fix for ctranslate2/faster-whisper not finding CUDA libs on Windows
import os
import torch
if os.name == 'nt' and torch.cuda.is_available():
    libs_path = os.path.join(os.path.dirname(torch.__file__), 'lib')
    if os.path.exists(libs_path):
        os.add_dll_directory(libs_path)

from modules.stt import STT
from modules.llm import LLM
from modules.tts import TTS
from modules.wake_word import WakeWord
from modules.vad import VAD
from modules.actions import Actions
from gui import ModernHUD

class CherryWorker(QThread):
    # Signals to update GUI
    sig_state = pyqtSignal(str) # "IDLE", "LISTENING", "THINKING", "SPEAKING"
    sig_text = pyqtSignal(str, str) # user_text, ai_text
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.actions = Actions()
        self.audio_queue = queue.Queue()
        
    def run(self):
        print("--- Initializing Cherry Core ---")
        self.sig_state.emit("IDLE")
        self.sig_text.emit("System Initializing...", "Loading Modules...")
        
        # Audio Settings
        self.sample_rate = 16000
        self.chunk_size = 1024 
        
        # Modules
        self.wake_word = WakeWord(keyword="hi")
        self.stt = STT()
        self.llm = LLM()
        self.tts = TTS()
        self.vad = VAD(threshold=0.02)
        
        self.is_listening = False
        self.audio_buffer = []
        self.wake_buffer = [] 
        
        print("--- Cherry is Ready. Say 'Hi' ---")
        self.sig_text.emit("System Online", "Ready. Say 'Hi'")
        
        # Open audio stream
        device_info = sd.query_devices(kind='input')
        print(f"Using Input Device: {device_info['name']}")

        with sd.InputStream(samplerate=self.sample_rate, 
                            blocksize=self.chunk_size, 
                            channels=1, 
                            callback=self.audio_callback):
            while self.running:
                # Process audio from the queue
                try:
                    audio_data = self.audio_queue.get(timeout=1)
                    self.process_audio(audio_data)
                except queue.Empty:
                    continue

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        # Push to queue to avoid blocking the audio thread
        self.audio_queue.put(indata.copy().squeeze())

    def process_audio(self, audio_data):
        # Prevent hearing itself
        if self.tts.is_busy():
            self.wake_buffer = []
            self.audio_buffer = []
            return

        # Debug: Show volume level periodically (every ~20 chunks) to verify mic
        rms = np.sqrt(np.mean(audio_data**2))
        if np.random.rand() < 0.1: # Print more frequently (10%)
            # Boost visualization sensitivity and show raw value
            bar_len = int(rms * 1000) 
            print(f"\rMic Level: {'|' * bar_len:<20} (RMS: {rms:.4f})", end='', flush=True)

        if not self.is_listening:
            # IDLE: Check for "Cherry"
            self.wake_buffer.append(audio_data)
            # Buffer ~1.5 seconds
            if len(self.wake_buffer) > 24:
                self.wake_buffer.pop(0)
                
                # Check every 0.5s (8 chunks)
                if len(self.wake_buffer) % 8 == 0:
                    combined_audio = np.concatenate(self.wake_buffer)
                    if self.wake_word.detect(combined_audio):
                        print("\n[!] Cherry detected!")
                        self.is_listening = True
                        self.audio_buffer = [] 
                        self.wake_buffer = []
                        
                        self.sig_state.emit("LISTENING")
                        self.sig_text.emit("Listening...", "")
                        self.tts.speak("Yes?")
        else:
            # ACTIVE: Listen until silence
            self.audio_buffer.append(audio_data)
            vad_status = self.vad.process_chunk(audio_data)
            
            if vad_status == 1: # Speech ended
                print("\n[!] Silence detected. Processing...")
                self.is_listening = False
                self.sig_state.emit("THINKING")
                
                # Capture full audio
                full_audio = np.concatenate(self.audio_buffer)
                self.process_command(full_audio)
                
                self.sig_state.emit("IDLE") 

    def process_command(self, audio_data):
        text = self.stt.transcribe(audio_data)
        if not text or len(text) < 2:
            print("No speech recognized.")
            self.sig_text.emit("...", "I didn't catch that.")
            return

        print(f"User: {text}")
        response = self.llm.chat(text)
        clean_response = self.handle_actions(response)
        
        self.sig_text.emit(text, clean_response)
        self.sig_state.emit("SPEAKING")
        self.tts.speak(clean_response)

    def handle_actions(self, response):
        import re
        if "[STATS]" in response:
            stats = self.actions.get_system_stats()
            response = response.replace("[STATS]", "") + f" {stats}"
        if "[TIME]" in response:
            time_str = self.actions.get_time()
            response = response.replace("[TIME]", "") + f" {time_str}"
        if "[DATE]" in response:
            date_str = self.actions.get_date()
            response = response.replace("[DATE]", "") + f" {date_str}"
        if "[MINIMIZE]" in response:
            self.actions.minimize_all()
            response = response.replace("[MINIMIZE]", "")
        if "[SCREENSHOT]" in response:
            result = self.actions.take_screenshot()
            response = response.replace("[SCREENSHOT]", "") + f" {result}"

        match = re.search(r"\[OPEN:\s*(.*?)\]", response)
        if match:
            self.actions.open_app(match.group(1))
            response = response.replace(match.group(0), "")
        match = re.search(r"\[SEARCH:\s*(.*?)\]", response)
        if match:
            self.actions.search_web(match.group(1))
            response = response.replace(match.group(0), "")
        match = re.search(r"\[PLAY:\s*(.*?)\]", response)
        if match:
            self.actions.play_youtube(match.group(1))
            response = response.replace(match.group(0), "")
        match = re.search(r"\[VOLUME:\s*(.*?)\]", response)
        if match:
            self.actions.adjust_volume(match.group(1))
            response = response.replace(match.group(0), "")
        return response.strip()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    worker = CherryWorker()
    
    worker.sig_state.connect(hud.set_state)
    worker.sig_text.connect(hud.set_text)
    
    hud.show()
    worker.start()
    sys.exit(app.exec())
