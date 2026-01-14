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
from modules.brain_agent import BrainAgent
from modules.tts import TTS
from modules.wake_word import WakeWord
from modules.vad import VAD
from modules.actions import Actions
from modules.vision import Vision
from modules.pulse import PulseWorker
from modules.emotion import EmotionEngine
from modules.vision_buffer import visual_buffer
from modules.clipboard import ClipboardMonitor
from modules.agency import cherry_agency
from config import settings
from gui import ModernHUD

class CherryWorker(QThread):
    # Signals to update GUI
    sig_state = pyqtSignal(str) # "IDLE", "LISTENING", "THINKING", "SPEAKING"
    sig_text = pyqtSignal(str, str) # user_text, ai_text
    sig_audio_level = pyqtSignal(float) # Normalized audio level (0.0 - 1.0)
    sig_task_update = pyqtSignal(int) # Number of active background tasks
    sig_tts_finished = pyqtSignal() # Internal signal for thread safety
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.actions = Actions()
        self.vision = Vision()
        self.pulse = PulseWorker()
        self.emotion = EmotionEngine()
        self.audio_queue = queue.Queue()
        self.last_proactive_time = 0
        self.follow_up_active = False
        self.follow_up_start = 0
        
        # Connect internal signal
        self.sig_tts_finished.connect(self.on_tts_finished)
        
    def run(self):
        print("--- Initializing Cherry Core ---")
        self.sig_state.emit("IDLE")
        
        # Start Passive Senses
        visual_buffer.start()
        self.clipboard = ClipboardMonitor(self.handle_clipboard_change)
        self.clipboard.start()
        
        # Connect Pulse Signal directly to TTS
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
        self.brain = BrainAgent()
        self.tts = TTS()
        self.tts.set_callback(self.trigger_tts_finished) # Set callback
        self.vad = VAD(threshold=settings['vad']['threshold'])
        
        self.is_listening = False
        self.audio_buffer = []
        
        print("--- Cherry is Ready. Say 'Hey Jarvis' or 'Alexa' ---")
        self.sig_text.emit("System Online", "Ready. Say 'Hey Jarvis'")
        
        # Find WASAPI Microphone
        devices = sd.query_devices()
        input_device_id = None
        for i, d in enumerate(devices):
            if 'WASAPI' in sd.query_hostapis(d['hostapi'])['name'] and d['max_input_channels'] > 0:
                if 'Microphone' in d['name']:
                    input_device_id = i
                    break
        
        if input_device_id is None:
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
                # Update Agency Status Periodically
                self.sig_task_update.emit(cherry_agency.task_queue.qsize())
                
                # Check Follow-up Timeout (e.g., 8 seconds)
                if self.follow_up_active:
                    if time.time() - self.follow_up_start > 8:
                        self.follow_up_active = False
                        if not self.is_listening:
                            print(">> Follow-up timeout. Returning to IDLE.")
                            self.sig_state.emit("IDLE")

                try:
                    audio_data = self.audio_queue.get(timeout=0.1)
                    self.process_audio(audio_data)
                except queue.Empty:
                    continue

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        new_length = int(len(indata) / self.downsample_factor)
        downsampled = scipy.signal.resample(indata, new_length)
        downsampled = downsampled.astype(np.float32)
        self.audio_queue.put(downsampled.squeeze())

    def trigger_tts_finished(self):
        """Callback from TTS thread. Emit signal to handle in main thread."""
        self.sig_tts_finished.emit()

    def on_tts_finished(self):
        """Called when TTS finishes speaking. Enter Follow-up Mode."""
        print(">> TTS Finished. Entering Follow-up Mode.")
        self.follow_up_active = True
        self.follow_up_start = time.time()
        
        # Automatically start listening without wake word
        self.is_listening = True
        self.audio_buffer = []
        self.sig_state.emit("LISTENING")
        # self.tts.play_listening_cue() # Optional: Might be annoying if beep happens every time

    def process_audio(self, audio_data):
        # Calculate RMS
        rms = np.sqrt(np.mean(audio_data**2))
        self.sig_audio_level.emit(float(rms))

        # --- BARGE-IN LOGIC ---
        # If TTS is busy, we ONLY listen for Wake Word to interrupt.
        if self.tts.is_busy():
            # Risk: Self-triggering if volume is loud.
            if self.wake_word.detect(audio_data):
                print("\n[!] Barge-In Detected! Stopping TTS.")
                self.tts.stop()
                self.is_listening = True
                self.audio_buffer = [] 
                self.sig_state.emit("LISTENING")
                self.tts.play_listening_cue()
            return # Skip normal VAD/processing while speaking

        # --- NORMAL LISTENING LOGIC ---
        if not self.is_listening:
            # Check for Wake Word OR Follow-up Speech
            wake_detected = self.wake_word.detect(audio_data)
            
            # If in Follow-up mode, check for just speech energy (VAD-ish) or Wake Word
            if self.follow_up_active:
                # Simple energy threshold for start of speech in follow-up
                # This is a crude VAD. Ideally, we use the VAD module.
                if wake_detected or (rms > 0.02): # Threshold for "User is speaking"
                    print("\n[!] Follow-up Speech Detected!")
                    self.is_listening = True
                    self.audio_buffer = [] 
                    self.sig_state.emit("LISTENING")
                    self.follow_up_active = False # Reset follow-up
            
            elif wake_detected:
                print("\n[!] Wake Word Detected!")
                self.is_listening = True
                self.audio_buffer = [] 
                self.sig_state.emit("LISTENING")
                self.sig_text.emit("Listening...", "")
                self.tts.play_listening_cue()
        else:
            # We are actively recording
            self.audio_buffer.append(audio_data)
            vad_status = self.vad.process_chunk(audio_data)
            
            if vad_status == 1: # Silence detected (End of Phrase)
                print("\n[!] Silence detected. Processing...")
                self.is_listening = False
                self.sig_state.emit("THINKING")
                
                full_audio = np.concatenate(self.audio_buffer)
                self.process_command(full_audio)
                # Note: We do NOT emit "IDLE" here. 
                # We wait for TTS to finish, which triggers on_tts_finished -> LISTENING again.

    def handle_proactive_speech(self, text):
        now = time.time()
        if now - self.last_proactive_time < 30: 
            return
        self.last_proactive_time = now
        self.sig_state.emit("SPEAKING")
        self.sig_text.emit("Cherry Proactive", text)
        self.tts.speak(text)

    def handle_clipboard_change(self, content):
        if content.startswith("http"):
            msg = f"Sir, I noticed you copied a link. Would you like me to research it for you?"
            self.handle_proactive_speech(msg)

    def process_command(self, audio_data):
        self.pulse.reset_idle_timer()
        text = self.stt.transcribe(audio_data)
        if not text or len(text) < 2:
            self.sig_text.emit("...", "I didn't catch that.")
            # If we didn't catch it, go back to follow-up listening?
            # Or just IDLE. Let's trigger follow-up to give them a second chance.
            self.on_tts_finished() 
            return

        print(f"User: {text}")
        
        # --- COMMAND INTERCEPTION ---
        # Handle "Sleep" / "Stop Listening" locally to force IDLE state
        sleep_triggers = ["go to sleep", "go to idle", "stop listening", "go mute", "sleep mode"]
        if any(trigger in text.lower() for trigger in sleep_triggers):
            print(">> [Command] Sleep Triggered.")
            self.sig_text.emit(text, "Going to sleep.")
            self.sig_state.emit("IDLE")
            self.follow_up_active = False # Cancel follow-up
            self.tts.speak("Going to sleep. Wake me if you need me.", voice="af_heart") # Neutral voice
            return

        # Handle "Shutdown" / "Exit"
        shutdown_triggers = ["shutdown yourself", "shutdown yourselves", "exit program", "terminate system", "self destruct"]
        if any(trigger in text.lower() for trigger in shutdown_triggers):
            print(">> [Command] Shutdown Triggered.")
            self.sig_text.emit(text, "Shutting down systems. Goodbye, Sir.")
            self.sig_state.emit("IDLE")
            self.tts.speak("Shutting down all neural links. Goodbye, Sir.", voice="af_heart")
            # Wait a moment for TTS to start/queue before killing process
            time.sleep(3)
            QApplication.instance().quit()
            return

        # 1. EMOTION
        mood = self.emotion.analyze(text, audio_data=audio_data)
        mood_directive = self.emotion.get_system_directive(mood)
        voice_settings = self.emotion.get_voice_settings(mood)
        
        self.brain.update_mood(mood_directive)

        # 2. VISION
        image_data = None
        vision_triggers = ["see", "look", "screen", "what is this", "read this", "describe"]
        if any(trigger in text.lower() for trigger in vision_triggers):
            image_data = self.vision.capture_screen()
            self.sig_text.emit(text, "Analyzing screen...")

        # 3. BRAIN
        response = self.brain.chat(text, image_data=image_data)
        
        # 4. SPEAK
        self.sig_text.emit(text, response)
        self.sig_state.emit("SPEAKING")
        
        self.tts.speak(
            response, 
            voice=voice_settings['voice'], 
            speed=voice_settings['speed']
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    worker = CherryWorker()
    
    # Connect all signals
    worker.sig_state.connect(hud.set_state)
    worker.sig_text.connect(hud.set_text)
    worker.sig_audio_level.connect(hud.update_audio_level)
    worker.sig_task_update.connect(hud.update_task_count)
    
    hud.show()
    worker.start()
    sys.exit(app.exec())

