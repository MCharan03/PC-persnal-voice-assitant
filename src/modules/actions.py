import os
import subprocess
import webbrowser
import psutil
import pyautogui

class Actions:
    def __init__(self):
        print("Action module initialized.")

    def open_app(self, app_name):
        """Attempts to open a common application."""
        app_name = app_name.lower()
        if "chrome" in app_name:
            os.startfile("chrome.exe")
        elif "notepad" in app_name:
            subprocess.Popen(["notepad.exe"])
        elif "code" in app_name or "vs code" in app_name:
            subprocess.Popen(["code"], shell=True)
        else:
            # Fallback: Try searching for it
            pyautogui.press('win')
            pyautogui.write(app_name)
            pyautogui.press('enter')
        return f"Attempting to open {app_name}."

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
