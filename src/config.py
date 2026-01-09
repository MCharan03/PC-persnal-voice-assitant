import yaml
import os

# Path to config/settings.yaml (relative to src/)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.yaml')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"Warning: Config file not found at {CONFIG_PATH}. Using defaults.")
        return {
            "system": {"native_rate": 48000, "target_rate": 16000},
            "vad": {"threshold": 0.0005},
            "wake_word": {"keyword": "hey jarvis"},
            "llm": {"model": "llama3.2"},
            "tts": {
                "model_path": "assets/models/kokoro-v1.0.onnx",
                "voices_path": "assets/models/voices-v1.0.bin",
                "voice_name": "af_heart"
            }
        }
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

# Singleton access
settings = load_config()
