import pyautogui
import base64
import io
import time

class Vision:
    def __init__(self):
        print("Vision Module Initialized.")
    
    def capture_screen(self):
        """
        Captures the current screen and returns it as a base64 encoded string.
        Returns None if capture fails.
        """
        try:
            # Capture full screen
            screenshot = pyautogui.screenshot()
            
            # Convert to bytes
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            
            # Encode to base64
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return img_str
        except Exception as e:
            print(f"Vision Error: {e}")
            return None

if __name__ == "__main__":
    v = Vision()
    s = v.capture_screen()
    print(f"Captured screenshot of size: {len(s)} bytes")
