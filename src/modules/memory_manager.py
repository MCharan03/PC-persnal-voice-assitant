import json
import os

class MemoryManager:
    def __init__(self, memory_file="data/memory.json", context_limit=10):
        self.memory_file = memory_file
        self.context_limit = context_limit
        self.conversation_history = []
        self.long_term_memory = {}
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.long_term_memory = data.get("facts", {})
            except Exception as e:
                print(f"Error loading memory: {e}")

    def save_memory(self):
        try:
            with open(self.memory_file, 'w') as f:
                json.dump({"facts": self.long_term_memory}, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def add_message(self, role, content):
        """Adds a message to the sliding window history."""
        self.conversation_history.append({"role": role, "content": content})
        # Keep only the system prompt + last N messages
        if len(self.conversation_history) > self.context_limit:
            # Assuming index 0 is system prompt, we pop from index 1
            if self.conversation_history[0]["role"] == "system":
                 # Keep system prompt (index 0), remove oldest user/assistant message (index 1)
                self.conversation_history.pop(1)
            else:
                self.conversation_history.pop(0)

    def get_context(self):
        """Returns the formatted messages list for Ollama."""
        # Inject long-term memory into the system prompt if needed
        # For now, we just return the sliding window
        return self.conversation_history

    def remember_fact(self, key, value):
        self.long_term_memory[key] = value
        self.save_memory()

    def recall_fact(self, key):
        return self.long_term_memory.get(key)
