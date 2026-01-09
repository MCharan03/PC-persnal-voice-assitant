import requests
import numpy as np
import soundfile as sf
import io

def create_dummy_wav():
    # Generate 1 second of silence/noise
    sr = 16000
    t = np.linspace(0, 1, sr, endpoint=False)
    # A simple sine wave to ensure it's not empty
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    
    mem_file = io.BytesIO()
    sf.write(mem_file, audio, sr, format='WAV')
    mem_file.seek(0)
    return mem_file

def test_api():
    url = "http://localhost:5000/api/voice"
    print(f"Testing {url}...")
    
    try:
        wav_file = create_dummy_wav()
        files = {'audio': ('test.wav', wav_file, 'audio/wav')}
        
        response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api()
