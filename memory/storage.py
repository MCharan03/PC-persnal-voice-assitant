import json
import os
from collections import deque
from utils.logger import logger

class Memory:
    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.memory_path = os.path.join(self.base_path, 'memory.json')
        self.workflows_path = os.path.join(self.base_path, 'workflows.json')
        self.memory = self._load_json(self.memory_path)
        self.workflows = self._load_json(self.workflows_path)
        
        # Short-term context (Last 5 interactions)
        self.context = deque(maxlen=5)
        # Recent actions for pattern detection
        self.action_history = deque(maxlen=10)

    def _load_json(self, path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return {}

    def add_interaction(self, user_input, response, intent_type):
        """Stores interaction for short-term context with validation for patterns."""
        self.context.append({
            "user": user_input,
            "assistant": response,
            "intent": intent_type
        })
        
        # Validation for pattern learning
        if intent_type in ["OPEN_APP", "RUN_COMMAND"]:
            if self._is_valid_for_workflow(user_input, response):
                self.action_history.append(user_input.lower().strip())

    def _is_valid_for_workflow(self, command, response):
        """Ensures only successful, complete commands are learned."""
        cmd = command.lower().strip()
        # Reject incomplete or failed commands
        if len(cmd.split()) < 2: return False
        if "couldn't find" in response.lower(): return False
        if "failed" in response.lower(): return False
        if "blocked" in response.lower(): return False
        return True

    def get_recent_context(self, n=3) -> str:
        """Returns the last n interactions for lightweight context."""
        recent = list(self.context)[-n:]
        history_str = ""
        for turn in recent:
            history_str += f"User: {turn['user']}\nSAMBA: {turn['assistant']}\n"
        return history_str

    def get_context(self) -> str:
        """Formats recent history for the LLM."""
        history_str = ""
        for turn in self.context:
            history_str += f"User: {turn['user']}\nSAMBA: {turn['assistant']}\n"
        return history_str

    def detect_patterns(self):
        """Detects if the last two actions have been performed together before."""
        if len(self.action_history) < 4:
            return None
        
        actions = list(self.action_history)
        current_pair = actions[-2:]
        
        # Search for this pair earlier in the history
        # (excluding the current pair itself)
        for i in range(len(actions) - 3):
            if actions[i:i+2] == current_pair:
                # Sequence repeated! Check if it's already a workflow
                for name, steps in self.workflows.items():
                    if steps == current_pair:
                        return None
                return current_pair
        return None

    def save_workflow(self, name, steps):
        self.workflows[name.lower()] = steps
        try:
            with open(self.workflows_path, 'w') as f:
                json.dump(self.workflows, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving workflow: {e}")
            return False

    def get_workflow(self, name):
        return self.workflows.get(name.lower())

    def save_memory(self):
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
