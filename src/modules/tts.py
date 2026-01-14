import threading
import queue
import time
import os
import io
import soundfile as sf
import numpy as np
import sounddevice as sd
from kokoro_onnx import Kokoro
from config import settings

class TTS:
    _instance = None
    _queue = queue.Queue()
    _worker_thread = None
    _is_busy = False 
    _cue_audio = None 
    _stop_flag = False 
    _current_voice = None
    _current_speed = 1.0
    _completion_callback = None
    _kokoro = None  # Model instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTS, cls).__new__(cls)
            cls._current_voice = settings['tts']['voice_name']
            cls._start_worker()
            cls._generate_cue()
        return cls._instance

    @classmethod
    def set_callback(cls, func):
        cls._completion_callback = func

    @classmethod
    def set_voice(cls, voice_name):
        cls._current_voice = voice_name

    @classmethod
    def set_speed(cls, speed):
        cls._current_speed = speed

    @classmethod
    def is_busy(cls):
        return cls._is_busy

    @classmethod
    def stop(cls):
        cls._stop_flag = True
        try:
            with cls._queue.mutex:
                cls._queue.queue.clear()
            sd.stop()
        except Exception as e:
            print(f"Error stopping TTS: {e}")

    @classmethod
    def _generate_cue(cls):
        try:
            fs = 44100
            duration = 0.2
            t = np.linspace(0, duration, int(fs * duration), endpoint=False)
            frequency = 880 
            audio = 0.3 * np.sin(2 * np.pi * frequency * t)
            audio += 0.3 * np.sin(2 * np.pi * (frequency * 2) * t) 
            audio *= np.exp(-10 * t) 
            cls._cue_audio = audio.astype(np.float32)
        except Exception as e:
            print(f"Error generating cue: {e}")

    @classmethod
    def _init_model(cls):
        if cls._kokoro: return
        model_path = settings['tts']['model_path']
        voices_path = settings['tts']['voices_path']
        if not os.path.exists(model_path) or not os.path.exists(voices_path):
            print(f"ERROR: Kokoro model files not found at {model_path}")
            return
        try:
            cls._kokoro = Kokoro(model_path, voices_path)
            print(f"Kokoro TTS initialized.")
        except Exception as e:
            print(f"Failed to initialize Kokoro: {e}")

    @classmethod
    def _start_worker(cls):
        if cls._worker_thread is None:
            cls._worker_thread = threading.Thread(target=cls._run_worker, daemon=True)
            cls._worker_thread.start()

    @classmethod
    def _run_worker(cls):
        cls._init_model()
        
        while True:
            try:
                text = cls._queue.get()
                if text is None: break 
                
                if not cls._kokoro:
                    cls._queue.task_done()
                    continue

                cls._is_busy = True 
                cls._stop_flag = False
                
                samples, sample_rate = cls._kokoro.create(
                    text, 
                    voice=cls._current_voice, 
                    speed=cls._current_speed, 
                    lang="en-us"
                )
                
                if not cls._stop_flag:
                    sd.play(samples, sample_rate)
                    duration = len(samples) / sample_rate
                    start_time = time.time()
                    while time.time() - start_time < duration:
                        if cls._stop_flag:
                            sd.stop()
                            break
                        time.sleep(0.1)
                
                cls._is_busy = False 
                cls._queue.task_done()
                
                if cls._queue.empty() and cls._completion_callback and not cls._stop_flag:
                    try:
                        cls._completion_callback()
                    except Exception:
                        pass
                        
            except Exception as e:
                cls._is_busy = False
                print(f"TTS Error: {e}")

    def speak(self, text, voice=None, speed=None):
        if voice: self.set_voice(voice)
        if speed: self.set_speed(speed)
        print(f"Cherry: {text}")
        self._queue.put(text)

    def generate_audio_bytes(self, text):
        """Generates audio and returns WAV bytes (without playing)."""
        if not self._kokoro: self._init_model()
        if not self._kokoro: return None
        
        try:
            samples, sample_rate = self._kokoro.create(
                text, 
                voice=self._current_voice, 
                speed=self._current_speed, 
                lang="en-us"
            )
            
            byte_io = io.BytesIO()
            sf.write(byte_io, samples, sample_rate, format='WAV')
            return byte_io.getvalue()
        except Exception as e:
            print(f"Generation Error: {e}")
            return None

    def play_listening_cue(self):
        if self._cue_audio is not None:
            try:
                sd.play(self._cue_audio, 44100)
            except Exception as e:
                print(f"Error playing cue: {e}")

    def play_listening_cue(self):
        if self._cue_audio is not None:
            try:
                sd.play(self._cue_audio, 44100)
            except Exception as e:
                print(f"Error playing cue: {e}")