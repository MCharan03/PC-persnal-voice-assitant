import logging
import sys
import time

class SAMBALogger:
    def __init__(self, name="SAMBA"):
        self.logger = logging.getLogger(name)
        self._timers = {}
        self._metrics = {}
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, msg): self.logger.info(msg)
    def error(self, msg): self.logger.error(msg)
    def debug(self, msg): self.logger.debug(msg)

    def start_timer(self, label):
        self._timers[label] = time.perf_counter()

    def end_timer(self, label):
        start_time = self._timers.pop(label, None)
        if start_time is None: return
        
        duration = time.perf_counter() - start_time
        self._metrics[label] = duration

    def get_summary(self):
        if not self._metrics: return ""
        
        summary = "\n[PERF SUMMARY]"
        for label, duration in self._metrics.items():
            if duration < 1.0:
                formatted = f"{int(duration * 1000)}ms"
            else:
                formatted = f"{duration:.2f}s"
            summary += f"\n{label.capitalize()}: {formatted}"
        
        self._metrics.clear()
        return summary

logger = SAMBALogger()
