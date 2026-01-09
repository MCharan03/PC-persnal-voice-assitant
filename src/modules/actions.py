import os
import subprocess
import webbrowser
import psutil
import pyautogui
import datetime
from pytubefix import Search

class Actions:
    def __init__(self):
        print("Action module initialized.")
        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def open_app(self, app_name):
        """Attempts to open a common application."""
        app_name = app_name.lower()
        if "chrome" in app_name:
            os.startfile("chrome.exe")
        elif "brave" in app_name:
            os.startfile("brave.exe")
        elif "notepad" in app_name:
            subprocess.Popen(["notepad.exe"])
        elif "code" in app_name or "vs code" in app_name:
            subprocess.Popen(["code"], shell=True)
        elif "discord" in app_name:
            pyautogui.press('win')
            time.sleep(0.1)
            pyautogui.write("Discord")
            pyautogui.press('enter')
        elif "steam" in app_name:
            os.startfile("steam://open/main")
        elif "spotify" in app_name:
            # Try default spotify path or shell command
            try:
                subprocess.Popen(["spotify"], shell=True)
            except:
                pyautogui.press('win')
                time.sleep(0.1)
                pyautogui.write("Spotify")
                pyautogui.press('enter')
        else:
            # Fallback: Try searching for it
            pyautogui.press('win')
            pyautogui.write(app_name)
            pyautogui.press('enter')
        return f"Attempting to open {app_name}."

    def control_media(self, command):
        """Controls system media playback."""
        command = command.lower()
        if "pause" in command or "play" in command:
            pyautogui.press('playpause')
            return "Toggling playback."
        elif "next" in command or "skip" in command:
            pyautogui.press('nexttrack')
            return "Skipping to next track."
        elif "previous" in command or "back" in command:
            pyautogui.press('prevtrack')
            return "Going back to previous track."
        return "I couldn't understand the media command."

    def get_system_stats(self):
        """Returns CPU, RAM, and Battery info."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        
        status = f"CPU usage is at {cpu}%. RAM usage is at {ram}%."
        if battery:
            status += f" Battery is at {battery.percent}%."
        return status

    def search_web(self, query):
        """Opens a web browser and searches."""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching for {query} on the web."
        
    def play_youtube(self, query):
        """Plays a video on YouTube."""
        try:
            print(f"Searching YouTube for: {query}")
            # Try to get the first video result
            s = Search(query)
            results = s.videos
            if results:
                first_video = results[0]
                url = first_video.watch_url
                webbrowser.open(url)
                return f"Playing {first_video.title} on YouTube."
            else:
                raise Exception("No results found")
        except Exception as e:
            print(f"YouTube Search Error: {e}. Falling back to generic search.")
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            return f"Opening YouTube search for {query}."

    def get_time(self):
        now = datetime.datetime.now()
        return f"It is currently {now.strftime('%I:%M %p')}."

    def get_date(self):
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

    def minimize_all(self):
        pyautogui.hotkey('win', 'd')
        return "Minimizing all windows."

    def take_screenshot(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
        pyautogui.screenshot(filename)
        return f"Screenshot saved."

    def adjust_volume(self, direction):
        """Adjusts system volume."""
        if "up" in direction:
            for _ in range(5): pyautogui.press('volumeup')
            return "Turning volume up."
        elif "down" in direction:
            for _ in range(5): pyautogui.press('volumedown')
            return "Turning volume down."
        elif "mute" in direction:
            pyautogui.press('volumemute')
            return "Muting volume."
        return "I couldn't understand the volume command."

if __name__ == "__main__":
    actions = Actions()
    print(actions.get_system_stats())
