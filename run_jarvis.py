import threading
import speech_recognition as sr
import pyttsx3
import time
from core.brain import process_command
# from app import app, socketio # We will import this if we want to run the server

# Initialize Voice
ear = sr.Recognizer()
mouth = pyttsx3.init()

# Configure mouth
voices = mouth.getProperty('voices')
# Try to set a female voice if available
for voice in voices:
    if "female" in voice.name.lower() or "zira" in voice.name.lower():
        mouth.setProperty('voice', voice.id)
        break
mouth.setProperty('rate', 170)

def speak(text):
    if not text: return
    print(f"Cherry: {text}")
    mouth.say(text)
    mouth.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        ear.adjust_for_ambient_noise(source)
        try:
            # Timeout for silence, phrase_time_limit for command length
            audio = ear.listen(source, timeout=5, phrase_time_limit=10)
            text = ear.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            # print("Could not understand audio")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

# Daemon Loop
def run_daemon():
    speak("Cherry OS Online. Waiting for command.")
    
    while True:
        command = listen()
        if command:
            # Wake word check (Optional)
            triggers = ["cherry", "jarvis", "assistant", "computer", "hello"]
            if any(trigger in command.lower() for trigger in triggers):
                # Remove trigger word
                # command = command.lower().replace("cherry", "").strip() 
                response = process_command(command)
                speak(response)

# Flask Server Thread
def run_server():
    # Import inside thread to avoid circular imports or early init
    from app import app, socketio
    socketio.run(app, port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Start Flask in a separate thread
    # server_thread = threading.Thread(target=run_server)
    # server_thread.daemon = True
    # server_thread.start()
    
    # Run Main Daemon
    run_daemon()
