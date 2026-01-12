import threading
import time
import psutil
from datetime import datetime

class PulseCore:
    def __init__(self, callback_func):
        """
        callback_func: function to call when an event triggers (e.g., emit to socket)
        """
        self.callback = callback_func
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.last_cpu_warning = 0
        self.start()
        print("Pulse (Proactive System Monitor) Started.")

    def start(self):
        self.thread.start()

    def _monitor_loop(self):
        while self.running:
            try:
                # 1. Check CPU (Proactive Health)
                cpu_usage = psutil.cpu_percent(interval=1)
                if cpu_usage > 90:
                    now = time.time()
                    if now - self.last_cpu_warning > 300: # Alert max once per 5 mins
                        self.last_cpu_warning = now
                        self.trigger_event(f"Sir, CPU usage is critical at {cpu_usage}%. Shall I optimize background processes?")

                # 2. Check Battery (if laptop)
                battery = psutil.sensors_battery()
                if battery and battery.percent < 20 and not battery.power_plugged:
                    # Simple duplicate check logic would go here
                    pass

                # 3. Time-based Greeting (Morning/Evening)
                # (Implementation omitted for brevity, but this is where "Good Morning" logic lives)

                time.sleep(5) # Tick every 5 seconds
            except Exception as e:
                print(f"Pulse Error: {e}")

    def trigger_event(self, message):
        print(f">> [Pulse] Triggering Proactive Message: {message}")
        if self.callback:
            self.callback(message)

if __name__ == "__main__":
    def test_cb(msg): print(f"CALLBACK: {msg}")
    p = PulseCore(test_cb)
    while True: time.sleep(1)