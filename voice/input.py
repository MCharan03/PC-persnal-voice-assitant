import speech_recognition as sr
from utils.normalizer import Normalizer
from utils.logger import logger

class VoiceInput:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.last_input = ""

    def listen(self) -> str:
        """Listens for speech with enhanced validation and noise filtering."""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                
                # Raw input debug log
                print(f"[RAW INPUT]: {text}")
                
                # 1. Basic validation
                if not text or len(text.strip()) < 3:
                    return None
                
                normalized = Normalizer.normalize(text)
                
                # 2. Repetition check (to prevent ghost triggers)
                if normalized == self.last_input:
                    return None
                
                self.last_input = normalized
                return normalized

            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return None
            except Exception as e:
                logger.debug(f"Speech recognition error: {e}")
                return None
