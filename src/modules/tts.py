import pyttsx3
import threading
import queue
import time

class TTS:
    _instance = None
    _queue = queue.Queue()
    _worker_thread = None
    _is_busy = False # New flag

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTS, cls).__new__(cls)
            cls._start_worker()
        return cls._instance

    @classmethod
    def is_busy(cls):
        return cls._is_busy

    @classmethod
    def _start_worker(cls):
        if cls._worker_thread is None:
            cls._worker_thread = threading.Thread(target=cls._run_worker, daemon=True)
            cls._worker_thread.start()
            print("TTS Worker started.")

    @classmethod
    def _run_worker(cls):
        """
        Runs in a dedicated thread. Initializes the engine locally 
        to ensure thread safety and sequential processing.
        """
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        engine.setProperty('volume', 0.9)
        
        # Try to find a male voice
        voices = engine.getProperty('voices')
        for voice in voices:
            if "male" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        while True:
            try:
                text = cls._queue.get()
                if text is None: break # Exit signal
                
                cls._is_busy = True # Set busy
                engine.say(text)
                engine.runAndWait()
                cls._is_busy = False # Done
                
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

if __name__ == "__main__":
    voice = TTS()
    voice.speak("System online.")
    voice.speak("All systems nominal.")
    time.sleep(5)
