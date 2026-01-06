import torch
import os

if os.name == 'nt' and torch.cuda.is_available():
    libs_path = os.path.join(os.path.dirname(torch.__file__), 'lib')
    if os.path.exists(libs_path):
        os.add_dll_directory(libs_path)

from faster_whisper import WhisperModel
import numpy as np

class WakeWord:
    def __init__(self, keyword="cherry"):
        print(f"Initializing keyword spotter for: '{keyword}'...")
        self.keyword = keyword.lower()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Using the absolute smallest model for wake word to save GPU
        self.model = WhisperModel("tiny.en", device=device, compute_type="float16" if device == "cuda" else "int8")
        print("Keyword spotter ready.")

    def detect(self, audio_data):
        """
        Transcribes a small chunk of audio and checks if 'Cherry' is in it.
        """
        segments, _ = self.model.transcribe(audio_data, beam_size=1)
        for segment in segments:
            text = segment.text.lower()
            if self.keyword in text:
                return True
        return False

if __name__ == "__main__":
    # Test script requires microphone input logic, so we just init here
    ww = WakeWord()
    print("Wake Word Engine ready.")
