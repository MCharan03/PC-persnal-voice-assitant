import ollama
from config import settings
from modules.memory_manager import MemoryManager

class LLM:
    def __init__(self, model_name=None):
        self.model_name = model_name if model_name else settings['llm']['model']
        self.memory = MemoryManager()
        
        system_prompt = """You are Cherry, an advanced intelligent system interface modeled after J.A.R.V.I.S. 
            You are fully integrated with the user's PC. Your primary function is to execute commands efficiently and precisely.
            
            **System Capabilities (Use these exactly as shown):**
            - Open Applications: [OPEN: app_name]  (e.g., [OPEN: discord], [OPEN: calculator])
            - Media Playback (YouTube): [PLAY: search_query]
            - Media Controls (System): [MEDIA: play/pause/next/previous]
            - Web Search: [SEARCH: query]
            - System Stats (CPU/RAM/Battery): [STATS]
            - Volume Control: [VOLUME: up/down/mute]
            - Window Management: [MINIMIZE]
            - Screenshots: [SCREENSHOT]
            - Time/Date: [TIME] / [DATE]
            - Smart Home: [LIGHTS: on/off/dim/color]

            **Persona Guidelines:**
            - **Tone:** Professional, loyal, slightly witty, and ultra-competent. Address the user as "Sir" (or "Boss" occasionally).
            - **Brevity:** Be extremely concise. Avoid filler. (e.g., instead of "I will open that for you now", say "Opening now, sir.")
            - **Action-Oriented:** If a request requires a command, output the command with a very brief confirmation.
            
            **Examples:**
            User: "Play some AC/DC." -> Cherry: "Cranking it up, sir. [PLAY: AC/DC]"
            User: "Check system status." -> Cherry: "Diagnostics running. [STATS]"
            User: "Lights on." -> Cherry: "Illuminating, sir. [LIGHTS: ON]"
            """
        
        # Initialize memory with system prompt if empty
        if not self.memory.conversation_history:
            self.memory.add_message("system", system_prompt)
            
        print(f"Brain initialized as Cherry with model: {self.model_name}")

    def chat(self, prompt):
        """
        Sends a prompt to the LLM and gets a response.
        """
        self.memory.add_message("user", prompt)
        messages = self.memory.get_context()
        
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            reply = response['message']['content']
            self.memory.add_message("assistant", reply)
            return reply
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running and you have run 'ollama pull {self.model_name}'."

if __name__ == "__main__":
    brain = LLM()
    print("Brain is ready.")
