import numpy as np

class VAD:
    def __init__(self, threshold=0.01, silence_duration=1.5, sample_rate=16000):
        self.threshold = threshold
        self.silence_limit = int(silence_duration * (sample_rate / 1024)) # approx chunks
        self.silence_counter = 0
        self.is_speaking = False
        
    def is_silent(self, audio_chunk):
        """
        Returns True if the audio chunk is considered silent (below threshold).
        """
        rms = np.sqrt(np.mean(audio_chunk**2))
        return rms < self.threshold

    def process_chunk(self, audio_chunk):
        """
        Returns:
        0: Continue listening (speech ongoing or waiting for silence to break)
        1: Stopped speaking (speech ended)
        2: No speech yet (silence continues)
        """
        silent = self.is_silent(audio_chunk)
        
        if not silent:
            self.is_speaking = True
            self.silence_counter = 0
            return 0 # Speech detected, keep recording
        
        if self.is_speaking and silent:
            self.silence_counter += 1
            if self.silence_counter > self.silence_limit:
                self.is_speaking = False
                self.silence_counter = 0
                return 1 # User stopped speaking
            return 0 # User is paused but might continue
            
        return 2 # Just background noise/silence
