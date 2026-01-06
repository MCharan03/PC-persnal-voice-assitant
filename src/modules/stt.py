import os
import torch

if os.name == 'nt' and torch.cuda.is_available():
    libs_path = os.path.join(os.path.dirname(torch.__file__), 'lib')
    if os.path.exists(libs_path):
        os.add_dll_directory(libs_path)

from faster_whisper import WhisperModel
import numpy as np

class STT:
    def __init__(self, model_size="small.en"):
        print(f"Initializing STT with model: {model_size}...")
        # Use CUDA for RTX 4050 speed
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = WhisperModel(model_size, device=device, compute_type="float16" if device == "cuda" else "int8")
        print("STT initialized successfully.")

    def transcribe(self, audio_data):
        """
        Transcribes audio data (numpy array) to text.
        """
        segments, info = self.model.transcribe(audio_data, beam_size=5)
        text = " ".join([segment.text for segment in segments]).strip()
        return text

if __name__ == "__main__":
    # Quick test if run directly
    stt = STT()
    print("STT is ready.")
