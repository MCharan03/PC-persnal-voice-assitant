import sys
import time
import queue
import numpy as np
import scipy.signal
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
from modules.vision import Vision
from modules.pulse import PulseWorker
from config import settings
from gui import ModernHUD

class CherryWorker(QThread):
    # Signals to update GUI
    sig_state = pyqtSignal(str) # "IDLE", "LISTENING", "THINKING", "SPEAKING"
    sig_text = pyqtSignal(str, str) # user_text, ai_text
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.actions = Actions()
        self.vision = Vision()
        self.pulse = PulseWorker()
        self.audio_queue = queue.Queue()
        
    def run(self):
        print("--- Initializing Cherry Core ---")
        self.sig_state.emit("IDLE")
        
        # Connect Pulse Signal directly to TTS
        # Note: We need a wrapper to also update GUI state if possible
        self.pulse.sig_proactive_speech.connect(self.handle_proactive_speech)
        self.pulse.start()

        self.sig_text.emit("System Initializing...", "Loading Modules...")
        
        # Audio Settings
        self.native_rate = settings['system']['native_rate']
        self.target_rate = settings['system']['target_rate']
        self.downsample_factor = int(self.native_rate / self.target_rate)
        self.chunk_size = 1024 * self.downsample_factor 
        
        # Modules
        self.wake_word = WakeWord(keyword=settings['wake_word']['keyword'])
        self.stt = STT()
        self.llm = LLM()
        self.tts = TTS()
        self.vad = VAD(threshold=settings['vad']['threshold'])
        
        self.is_listening = False
        self.audio_buffer = []
        # self.wake_buffer = [] # No longer needed for openWakeWord
        
        print("--- Cherry is Ready. Say 'Hey Jarvis' or 'Alexa' ---")
        self.sig_text.emit("System Online", "Ready. Say 'Hey Jarvis'")
        
        # Find WASAPI Microphone
        devices = sd.query_devices()
        input_device_id = None
        for i, d in enumerate(devices):
            if 'WASAPI' in sd.query_hostapis(d['hostapi'])['name'] and d['max_input_channels'] > 0:
                # Prefer Microphone Array if multiple
                if 'Microphone' in d['name']:
                    input_device_id = i
                    break
        
        if input_device_id is None:
            # Fallback to default
            input_device_id = sd.default.device[0]
            print("WASAPI Mic not found, using default.")
        
        device_info = devices[input_device_id]
        print(f"Using Input Device: {device_info['name']} (ID: {input_device_id}) @ {self.native_rate}Hz")

        with sd.InputStream(device=input_device_id,
                            samplerate=self.native_rate, 
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
        
        # High-quality resampling using Fourier method
        # Calculates new length based on ratio
        new_length = int(len(indata) / self.downsample_factor)
        downsampled = scipy.signal.resample(indata, new_length)
        
        # Cast to float32 (Whisper expects float32)
        downsampled = downsampled.astype(np.float32)
        
        # Push to queue to avoid blocking the audio thread
        self.audio_queue.put(downsampled.squeeze())

    def process_audio(self, audio_data):
        # Prevent hearing itself
        if self.tts.is_busy():
            self.audio_buffer = []
            return

        # Debug: Show volume level periodically (every ~20 chunks) to verify mic
        rms = np.sqrt(np.mean(audio_data**2))
        if np.random.rand() < 0.1: # Print more frequently (10%)
            # Boost visualization sensitivity and show raw value
            bar_len = int(rms * 50000) 
            print(f"\rMic Level: {'|' * bar_len:<20} (RMS: {rms:.6f})", end='', flush=True)

        if not self.is_listening:
            # IDLE: Feed every chunk to OpenWakeWord
            # OpenWakeWord expects ~80ms chunks (1280 samples @ 16k)
            # Our chunks are ~1024 samples. This is close enough for streaming.
            
            if self.wake_word.detect(audio_data):
                print("\n[!] Wake Word Detected!")
                self.is_listening = True
                self.audio_buffer = [] 
                
                self.sig_state.emit("LISTENING")
                self.sig_text.emit("Listening...", "")
                self.tts.play_listening_cue() # Instant beep
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

    def handle_proactive_speech(self, text):
        self.sig_state.emit("SPEAKING")
        self.sig_text.emit("System Alert", text)
        self.tts.speak(text)
        # Return to IDLE after a delay? TTS handles speaking, but GUI might get stuck.
        # Ideally, TTS should emit a 'finished' signal. For now, this is okay.

    def process_command(self, audio_data):
        self.pulse.reset_idle_timer() # Reset idle timer on activity
        text = self.stt.transcribe(audio_data)
        if not text or len(text) < 2:
            print("No speech recognized.")
            self.sig_text.emit("...", "I didn't catch that.")
            return

        print(f"User: {text}")
        
        # Check for visual intent
        image_data = None
        vision_triggers = ["see", "look", "screen", "what is this", "read this", "describe"]
        if any(trigger in text.lower() for trigger in vision_triggers):
            print("[Vision] Trigger detected. Capturing screen...")
            image_data = self.vision.capture_screen()
            self.sig_text.emit(text, "Analyzing screen...")

        response = self.llm.chat(text, image_data=image_data)
        
        # Handle Agent Tool Calls
        if isinstance(response, dict) and response.get("type") == "tool":
            tool_calls = response.get("calls", [])
            final_output = ""
            
            for tool in tool_calls:
                func_name = tool.function.name
                args = tool.function.arguments
                
                # Execute Tool
                result = self.actions.execute_tool_call(func_name, args)
                
                # Generate a natural language confirmation
                # In a full agent loop, we would feed this 'result' back to the LLM
                # For now, we just speak the result.
                final_output += str(result) + " "
                
            self.sig_text.emit(text, final_output)
            self.sig_state.emit("SPEAKING")
            self.tts.speak(final_output)
            
        else:
            # Fallback for Text / Regex
            # response is a dict with type="text" or a raw string (legacy)
            if isinstance(response, dict):
                response_text = response.get("content", "")
            else:
                response_text = str(response)
                
            clean_response = self.actions.parse_and_execute(response_text)
            
            self.sig_text.emit(text, clean_response)
            self.sig_state.emit("SPEAKING")
            self.tts.speak(clean_response)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    worker = CherryWorker()
    
    worker.sig_state.connect(hud.set_state)
    worker.sig_text.connect(hud.set_text)
    
    hud.show()
    worker.start()
    sys.exit(app.exec())
