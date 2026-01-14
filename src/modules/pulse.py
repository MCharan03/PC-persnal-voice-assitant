import time
import psutil
from PyQt6.QtCore import QThread, pyqtSignal
try:
    import pygetwindow as gw
except ImportError:
    gw = None
    print("Warning: pygetwindow not found. Context awareness disabled.")

class PulseWorker(QThread):
    sig_proactive_speech = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.last_cpu_warning = 0
        self.last_context_check = 0
        self.current_context = "Unknown"
        self.idle_timer_start = time.time()
        print("Pulse (Proactive System Monitor) Initialized.")

    def reset_idle_timer(self):
        self.idle_timer_start = time.time()

    def get_active_context(self):
        if not gw: return "Unknown"
        try:
            window = gw.getActiveWindow()
            if window:
                title = window.title.lower()
                if any(x in title for x in ['code', 'pycharm', 'studio', 'terminal', 'cmd', 'powershell']):
                    return "Coding"
                if any(x in title for x in ['chrome', 'edge', 'firefox', 'brave']):
                    return "Browsing"
                if any(x in title for x in ['discord', 'slack', 'teams']):
                    return "Communicating"
                if any(x in title for x in ['steam', 'game', 'play', 'unity', 'unreal']):
                    return "Gaming"
                return "General Use"
        except Exception:
            return "Unknown"
        return "Unknown"

    def run(self):
        print("Pulse Monitor Started.")
        while self.running:
            try:
                # 1. Check CPU (Proactive Health)
                cpu_usage = psutil.cpu_percent(interval=1)
                if cpu_usage > 90:
                    now = time.time()
                    if now - self.last_cpu_warning > 300: # Alert max once per 5 mins
                        self.last_cpu_warning = now
                        self.sig_proactive_speech.emit(f"Sir, CPU usage is critical at {cpu_usage}%. Shall I optimize background processes?")

                # 2. Check Context (Sentience)
                now = time.time()
                if now - self.last_context_check > 10: # Check every 10 seconds
                    self.last_context_check = now
                    new_context = self.get_active_context()
                    
                    if new_context != self.current_context and new_context != "Unknown":
                        # Context Switch Detected
                        print(f"Pulse: Context switched to {new_context}")
                        self.current_context = new_context
                        
                        # Proactive Comment on Switch (Rarely)
                        # We don't want to spam, so we use a probability or timer
                        # For now, let's just log it. In future, we can speak.
                        if new_context == "Gaming":
                             self.sig_proactive_speech.emit("I see we are gaming, Sir. I will minimize interruptions. Good luck.")

                # 3. Idle Chatter (Optional "Sentience")
                if time.time() - self.idle_timer_start > 3600: # 1 hour of silence
                    if self.current_context == "Coding":
                        self.sig_proactive_speech.emit("You have been coding for a while, Sir. Do not forget to hydrate.")
                    else:
                        self.sig_proactive_speech.emit("It has been quiet for a while. Is there anything I can help you with?")
                    self.reset_idle_timer()

                time.sleep(5) # Tick every 5 seconds
            except Exception as e:
                print(f"Pulse Error: {e}")
                time.sleep(5)

    def stop(self):
        self.running = False
