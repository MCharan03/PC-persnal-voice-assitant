import os
import torch

if os.name == 'nt' and torch.cuda.is_available():
    libs_path = os.path.join(os.path.dirname(torch.__file__), 'lib')
    if os.path.exists(libs_path):
        os.add_dll_directory(libs_path)

from faster_whisper import WhisperModel
import numpy as np

class STT:
    def __init__(self, model_size="base.en"):
        print(f"Initializing Main Speech-to-Text (STT) Engine...")
        
        # Use CUDA for RTX 4050 speed
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"
            print(">> STT using GPU (CUDA) for high-speed transcription.")
        else:
            device = "cpu"
            compute_type = "int8"
            print(">> STT using CPU (GPU not found).")
            
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("STT initialized successfully.")

    def transcribe(self, audio_data):
        """
        Transcribes audio data to text.
        
        Args:
            audio_data: Can be a file path (str), a binary file-like object (BytesIO), 
                        or a numpy array (np.ndarray).
        """
        # Reduced beam_size from 5 to 1 for speed
        segments, info = self.model.transcribe(audio_data, beam_size=1)
        text = " ".join([segment.text for segment in segments]).strip()
        return text

if __name__ == "__main__":
    # Quick test if run directly
    stt = STT()
    print("STT is ready.")
