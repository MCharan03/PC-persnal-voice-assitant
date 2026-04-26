import json
import requests
import re
from utils.config_loader import config
from utils.logger import logger

class IntentParser:
    def __init__(self, memory=None):
        self.memory = memory
        self.url = config.get("ollama_url", "http://localhost:11434/api/generate")
        self.model = config.get("model", "llama3:latest")
        
        # Recognized verbs
        self.verbs = ["open", "launch", "start", "run", "execute", "close", "stop", "exit"]

    def detect_intent(self, user_input: str) -> dict:
        """Fast-first hybrid intent detection with verb propagation."""
        user_input = user_input.lower().strip()

        # 1. Multi-command handling with verb propagation
        if any(sep in user_input for sep in [" and ", " then ", ", "]):
            parts = re.split(r' and | then |, ', user_input)
            parts = [p.strip() for p in parts if p.strip()]
            
            if not parts:
                return {"type": "CHAT", "data": {"query": user_input}}

            # Extract verb from the first part
            first_word = parts[0].split()[0] if parts[0] else ""
            main_verb = first_word if first_word in self.verbs else None
            
            final_commands = []
            for i, part in enumerate(parts):
                if i == 0:
                    final_commands.append(part)
                    continue
                
                # Check if this part starts with a known verb
                current_verb = part.split()[0] if part else ""
                if current_verb not in self.verbs and main_verb:
                    final_commands.append(f"{main_verb} {part}")
                else:
                    final_commands.append(part)
            
            return {"type": "MULTI", "commands": final_commands}

        # 2. Rule-based triggers (0ms latency)
        # Workflows
        if self.memory and self.memory.get_workflow(user_input):
            return {"type": "WORKFLOW", "data": {"name": user_input}}

        # Open App
        for v in ["open", "launch", "start"]:
            if user_input.startswith(v + " "):
                return {"type": "OPEN_APP", "data": {"app_name": user_input[len(v):].strip()}}

        # Close App
        for v in ["close", "stop", "exit"]:
            if user_input.startswith(v + " "):
                target = user_input[len(v):].strip()
                if target.endswith(" app"): target = target[:-4].strip()
                return {"type": "CLOSE_APP", "data": {"app_name": target}}

        # Run Command
        for v in ["run", "execute"]:
            if user_input.startswith(v + " "):
                return {"type": "RUN_COMMAND", "data": {"command": user_input[len(v):].strip()}}

        # 3. LLM Fallback (only for complex chat/reasoning)
        return self._llm_detect(user_input)

    def _llm_detect(self, user_input: str) -> dict:
        """Slower fallback for general chat."""
        # Note: We skip LLM for known dangerous patterns in main.py
        prompt = (
            "Classify intent: CHAT, OPEN_APP, RUN_COMMAND, WORKFLOW, CLOSE_APP.\n"
            "JSON ONLY: {\"type\": \"TYPE\", \"target\": \"extracted value or null\"}\n"
            f"Input: {user_input}"
        )

        try:
            payload = {"model": self.model, "prompt": prompt, "stream": False, "format": "json"}
            response = requests.post(self.url, json=payload, timeout=3)
            result = response.json().get("response", "{}")
            intent_data = json.loads(result)
            
            t = intent_data.get("type")
            target = intent_data.get("target")
            if t == "OPEN_APP": intent_data["data"] = {"app_name": target}
            elif t == "CLOSE_APP": intent_data["data"] = {"app_name": target}
            elif t == "RUN_COMMAND": intent_data["data"] = {"command": target}
            elif t == "WORKFLOW": intent_data["data"] = {"name": target or user_input}
            else: intent_data["type"] = "CHAT"; intent_data["data"] = {"query": user_input}
            
            return intent_data
        except:
            return {"type": "CHAT", "data": {"query": user_input}}
