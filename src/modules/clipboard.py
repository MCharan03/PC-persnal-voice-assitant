import threading
import time
import pyperclip

class ClipboardMonitor(threading.Thread):
    def __init__(self, callback):
        super().__init__(daemon=True)
        self.callback = callback
        self.last_clipboard = ""
        self.running = True
        print("Clipboard Monitor initialized.")

    def run(self):
        while self.running:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != self.last_clipboard:
                    self.last_clipboard = current_clipboard
                    if current_clipboard.strip():
                        print(f">> [Sense] Clipboard changed: {current_clipboard[:50]}...")
                        self.callback(current_clipboard)
            except Exception as e:
                # print(f"Clipboard Error: {e}")
                pass
            time.sleep(1.5)

    def stop(self):
        self.running = False
