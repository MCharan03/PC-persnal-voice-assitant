import os
import subprocess
import webbrowser
import platform
import pyautogui

# 1. File System Access
def read_file(filepath):
    """Reads any file on your PC"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

def write_file(filepath, content):
    """Writes code/notes to your PC"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return "File saved."
    except Exception as e:
        return f"Error writing file: {e}"

# 2. App & Web Control
def open_app(app_name):
    """Opens applications like Chrome, VS Code, Spotify"""
    system = platform.system()
    try:
        if system == "Windows":
            # Using 'start' is usually better in cmd, but os.system might need full path if not in PATH.
            # Using os.startfile is more robust on Windows.
            try:
                os.startfile(app_name)
            except:
                os.system(f"start {app_name}")
        elif system == "Darwin": # Mac
            os.system(f"open -a {app_name}")
        elif system == "Linux":
            os.system(f"xdg-open {app_name}")
        return f"Opening {app_name}..."
    except Exception as e:
        return f"Error opening app: {e}"
    
def google_search(query):
    """Browses the real internet"""
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching for {query}..."

# 3. System Vision (Screenshots)
def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        # Save to static folder if it exists, else root
        save_path = "vision_input.jpg"
        screenshot.save(save_path)
        return save_path
    except Exception as e:
        return f"Error taking screenshot: {e}"
