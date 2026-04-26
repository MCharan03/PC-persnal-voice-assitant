import pyttsx3
from utils.logger import logger

class VoiceOutput:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            # Set Jarvis-like properties
            self.engine.setProperty('rate', 180)    # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            
            # Select voice (prefer Male if available for Jarvis persona)
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "male" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            logger.error(f"TTS Initialization error: {e}")
            self.engine = None

    def speak(self, text: str):
        """Converts text to speech."""
        if not self.engine or not text:
            return
            
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS playback error: {e}")
