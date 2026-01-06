import pyttsx3
import threading

class TTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        # Set property before adding anything to queue
        self.engine.setProperty('rate', 175)    # Speed percent
        self.engine.setProperty('volume', 0.9)  # Volume 0-1
        
        voices = self.engine.getProperty('voices')
        # Try to find a male voice for Jarvis
        for voice in voices:
            if "male" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        print("Voice initialized.")

    def speak(self, text):
        """
        Speaks the given text in a separate thread to avoid blocking the UI.
        """
        print(f"Jarvis: {text}")
        
        def run():
            # Create a local engine instance for the thread if needed, 
            # but pyttsx3 usually prefers main thread.
            # For simplicity in this first version:
            self.engine.say(text)
            self.engine.runAndWait()
            
        threading.Thread(target=run).start()

if __name__ == "__main__":
    voice = TTS()
    voice.speak("Hello. I am Jarvis. Your personal AI assistant.")
