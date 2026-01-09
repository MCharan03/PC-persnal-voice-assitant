import threading
import queue
import time
import os
import numpy as np
import sounddevice as sd
from kokoro_onnx import Kokoro
from config import settings

class TTS:
    _instance = None
    _queue = queue.Queue()
    _worker_thread = None
    _is_busy = False 
    _cue_audio = None # Pre-generated buffer

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTS, cls).__new__(cls)
            cls._start_worker()
            cls._generate_cue()
        return cls._instance

    @classmethod
    def is_busy(cls):
        return cls._is_busy

    @classmethod
    def _generate_cue(cls):
        """Pre-generates the 'ding' sound."""
        try:
            fs = 44100
            duration = 0.2
            t = np.linspace(0, duration, int(fs * duration), endpoint=False)
            
            # Generate a pleasant "ding"
            frequency = 880 
            audio = 0.3 * np.sin(2 * np.pi * frequency * t)
            audio += 0.3 * np.sin(2 * np.pi * (frequency * 2) * t) 
            audio *= np.exp(-10 * t) 
            
            cls._cue_audio = audio.astype(np.float32)
        except Exception as e:
            print(f"Error generating cue: {e}")

    @classmethod
    def _start_worker(cls):
        if cls._worker_thread is None:
            cls._worker_thread = threading.Thread(target=cls._run_worker, daemon=True)
            cls._worker_thread.start()
            print("TTS Worker (Kokoro) started.")

    @classmethod
    def _run_worker(cls):
        """
        Runs in a dedicated thread. Initializes Kokoro-ONNX locally.
        """
        model_path = settings['tts']['model_path']
        voices_path = settings['tts']['voices_path']
        
        if not os.path.exists(model_path) or not os.path.exists(voices_path):
            print(f"ERROR: Kokoro model files not found at {model_path}")
            return

        try:
            kokoro = Kokoro(model_path, voices_path)
            # Default voice
            voice_name = settings['tts']['voice_name']
            print(f"Kokoro TTS initialized with voice: {voice_name}")
        except Exception as e:
            print(f"Failed to initialize Kokoro: {e}")
            return
        
        while True:
            try:
                text = cls._queue.get()
                if text is None: break 
                
                cls._is_busy = True 
                
                # Generate audio with Kokoro
                samples, sample_rate = kokoro.create(text, voice=voice_name, speed=1.0, lang="en-us")
                
                # Play audio
                sd.play(samples, sample_rate)
                sd.wait() # Wait for playback to finish
                
                cls._is_busy = False 
                cls._queue.task_done()
            except Exception as e:
                cls._is_busy = False
                print(f"TTS Error: {e}")

    def speak(self, text):
        """
        Queues the text to be spoken. Non-blocking.
        """
        print(f"Cherry: {text}")
        self._queue.put(text)

    def play_listening_cue(self):
        """
        Plays the pre-generated 'ding' sound instantly.
        """
        if self._cue_audio is not None:
            try:
                sd.play(self._cue_audio, 44100)
            except Exception as e:
                print(f"Error playing cue: {e}")

if __name__ == "__main__":
    voice = TTS()
    voice.speak("System online.")
    voice.speak("All systems nominal.")
    time.sleep(5)
