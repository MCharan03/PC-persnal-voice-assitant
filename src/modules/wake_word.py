import torch
import os

# We no longer need the CUDA injection here as we are forcing CPU for wake word
from faster_whisper import WhisperModel
import numpy as np

class WakeWord:
    def __init__(self, keyword="cherry"):
        print(f"Initializing Wake Word Engine (CPU Optimized) for: '{keyword}'...")
        self.keyword = keyword.lower()
        
        # Optimization: Run Wake Word on CPU to save GPU VRAM for the LLM & Main STT
        # 'tiny.en' is extremely fast on CPU (int8)
        device = "cpu" 
        compute_type = "int8"
        
        try:
            self.model = WhisperModel("tiny.en", device=device, compute_type=compute_type)
            print(f"Wake Word Monitor running on {device.upper()} (lightweight).")
        except Exception as e:
            print(f"Error initializing Wake Word: {e}")
            self.model = None

    def detect(self, audio_data):
        """
        Transcribes a small chunk of audio and checks if 'Hi' is in it.
        """
        if not self.model: return False
        
        # Variations allowed (Jarvis is more distinct than Hi)
        triggers = ["jarvis", "service", "jervis"]
        
        try:
            segments, _ = self.model.transcribe(audio_data, beam_size=1)
            for segment in segments:
                text = segment.text.lower().strip()
                # Remove punctuation
                import string
                text = text.translate(str.maketrans('', '', string.punctuation))
                
                print(f"Heard: '{text}'") # Debug enabled
                
                # Check for exact match of short words to avoid false positives inside other words
                words = text.split()
                if any(word in triggers for word in words):
                    return True
                    
        except Exception as e:
            print(f"Wake Word Error: {e}")
            
        return False

if __name__ == "__main__":
    ww = WakeWord()
    print("Wake Word Engine ready.")
