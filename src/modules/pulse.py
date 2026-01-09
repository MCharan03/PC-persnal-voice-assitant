import threading
import time
import psutil
import datetime
from PyQt6.QtCore import QThread, pyqtSignal

class PulseWorker(QThread):
    """
    The 'Pulse' thread monitors system state and user inactivity.
    It gives Cherry the ability to speak proactively.
    """
    sig_proactive_speech = pyqtSignal(str) # Emits message for TTS
    
    def __init__(self, idle_threshold_minutes=30):
        super().__init__()
        self.running = True
        self.idle_threshold = idle_threshold_minutes * 60
        self.last_activity_time = time.time()
        self.last_speech_time = time.time()
        
    def run(self):
        print("[Pulse] Background Monitor Started.")
        while self.running:
            try:
                # Check System Stats
                battery = psutil.sensors_battery()
                
                # Proactive Trigger 1: Low Battery
                if battery and battery.percent < 20 and not battery.power_plugged:
                    if time.time() - self.last_speech_time > 300: # Don't spam (5 min cooldown)
                        self.trigger_speech("Sir, battery levels are critical. Please connect a power source.")

                # Proactive Trigger 2: High CPU (Thermal Warning)
                # (Skipped for now to avoid false positives during gaming)

                # Update Idle Timer (This is a simplified idle check; 
                # real idle check requires hooking into OS input events which is complex)
                # For now, we simulate "idle" as "Time since last Voice Command"
                
                # Check Loop Speed
                time.sleep(10) 
            except Exception as e:
                print(f"[Pulse] Error: {e}")
                time.sleep(60)

    def trigger_speech(self, text):
        print(f"[Pulse] Triggering Proactive Speech: {text}")
        self.sig_proactive_speech.emit(text)
        self.last_speech_time = time.time()

    def reset_idle_timer(self):
        self.last_activity_time = time.time()
