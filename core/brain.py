import requests
import json
from utils.config_loader import config
from utils.logger import logger

class Brain:
    def __init__(self, memory=None, executor=None):
        self.url = config.get("ollama_url", "http://localhost:11434/api/generate")
        self.model = config.get("model", "llama3")
        self.system_prompt = (
            "You are SAMBA, a calm, intelligent personal assistant like Jarvis. "
            "Your responses should be short, professional, and confident. "
            "Never be verbose. Assist the user with their requests efficiently."
        )

    def think(self, user_input: str, context: str = "") -> str:
        prompt = f"{self.system_prompt}\n\nRecent History:\n{context}\nUser: {user_input}\nSAMBA:"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.url, json=payload, timeout=config.get("timeout", 15))
            response.raise_for_status()
            return response.json().get("response", "I'm sorry, I couldn't process that.").strip()
        except requests.exceptions.ConnectionError:
            return "I'm having trouble connecting to my cognitive engines (Ollama). Please ensure the service is running."
        except requests.exceptions.Timeout:
            return "The request to my brain timed out. I may be processing too much at once."
        except Exception as e:
            logger.error(f"Brain Error: {e}")
            return "I've encountered an internal cognitive error."
