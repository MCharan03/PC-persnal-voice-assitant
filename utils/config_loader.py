import json
import os

class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        try:
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = {}

    def get(self, key, default=None):
        return self._config.get(key, default)

config = ConfigLoader()
