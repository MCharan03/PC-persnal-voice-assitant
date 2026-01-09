import os
import numpy as np
from openwakeword.model import Model

class WakeWord:
    def __init__(self, keyword="hey jarvis"):
        print(f"Initializing Wake Word Engine (OpenWakeWord) for: '{keyword}'...")
        self.keyword = keyword
        
        # Load pre-trained models
        # We can load multiple models at once
        # Explicitly use 'onnx' inference framework since tflite-runtime is not available on Python 3.13
        self.model = Model(
            wakeword_models=["hey_jarvis", "alexa"],
            inference_framework="onnx"
        )
        print("Wake Word Monitor running on CPU (OpenWakeWord Optimized).")

    def detect(self, audio_data):
        """
        Feeds audio data to OpenWakeWord and returns True if a wake word is detected.
        Expects audio_data to be a numpy array of int16 or float32.
        """
        if not self.model: return False
        
        try:
            # OpenWakeWord expects 16-bit PCM (int16) scaled -32768 to 32767
            # Our audio is float32 (-1.0 to 1.0). Convert it.
            if audio_data.dtype == np.float32:
                audio_int16 = (audio_data * 32767).astype(np.int16)
            else:
                audio_int16 = audio_data

            # Feed the model (it handles its own buffering internally)
            prediction = self.model.predict(audio_int16)
            
            # Check results
            for mdl in self.model.prediction_buffer.keys():
                # Get the score for the last chunk
                scores = list(self.model.prediction_buffer[mdl])
                if scores and scores[-1] > 0.5: # Threshold 0.5
                    print(f"Wake Word Detected: {mdl} (Score: {scores[-1]:.2f})")
                    self.model.reset() # Reset internal state
                    return True
                    
        except Exception as e:
            print(f"Wake Word Error: {e}")
            
        return False

if __name__ == "__main__":
    ww = WakeWord()
    print("Wake Word Engine ready.")
