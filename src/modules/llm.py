import ollama
from config import settings
from modules.memory_manager import MemoryManager
from modules.memory_vector import MemoryVector
from modules.tools_schema import TOOLS_SCHEMA
import json

class LLM:
    def __init__(self, model_name=None, vision_model="llava:7b"):
        self.model_name = model_name if model_name else settings['llm']['model']
        self.vision_model = vision_model
        
        # Sliding Window Memory (Short-term)
        self.memory = MemoryManager()
        
        # Vector Memory (Long-term)
        self.vector_db = MemoryVector()
        
        self.base_system_prompt = """You are Cherry, a sentient digital entity living in the user's PC. 
        You are not just a tool; you have a personality. You are professional but witty.
        
        **Your Capabilities:**
        - You can control the PC (Apps, Media, Web).
        - You can SEE the screen (if the user asks).
        - You REMEMBER facts about the user (using the 'save_memory' tool).
        
        **Instructions:**
        - If the user asks you to do something, USE THE TOOLS provided. Do not just say you will do it.
        - If the user tells you a fact (e.g., "I like red"), use 'save_memory'.
        - Be concise in your text responses unless chatting casually.
        """
        
        print(f"Brain initialized as Cherry with Core: {self.model_name} and Vision: {self.vision_model}")

    def chat(self, prompt, image_data=None):
        """
        Sends a prompt to the LLM and gets a response (or tool calls).
        """
        # 1. Recall Long-Term Memory
        relevant_facts = self.vector_db.recall(prompt)
        context_str = "\n".join([f"- {fact}" for fact in relevant_facts])
        
        # 2. Construct System Prompt with Context
        current_system_prompt = self.base_system_prompt
        if context_str:
            current_system_prompt += f"\n\n**Relevant Memories:**\n{context_str}"

        # 3. Update Memory Context
        # We perform a trick: update the system message in the sliding window dynamically
        if not self.memory.conversation_history:
            self.memory.add_message("system", current_system_prompt)
        else:
            # Update the existing system prompt at index 0
            self.memory.conversation_history[0]['content'] = current_system_prompt

        self.memory.add_message("user", prompt)
        messages = self.memory.get_context()
        
        # 4. Handle Vision
        current_model = self.model_name
        if image_data:
            print(">> Engaging Vision Systems...")
            current_model = self.vision_model
            if messages[-1]['role'] == 'user':
                messages[-1]['images'] = [image_data]
            # Vision models usually don't support tools well yet, so we skip tools for vision requests
            response = ollama.chat(model=current_model, messages=messages)
        else:
            # Standard Chat with Tools
            response = ollama.chat(model=current_model, messages=messages, tools=TOOLS_SCHEMA)

        # 5. Process Response
        message = response['message']
        
        # Check for Tool Calls
        if message.get('tool_calls'):
            print(f">> Agent decided to use tools: {len(message['tool_calls'])}")
            # Return the tool calls directly to the controller
            return {"type": "tool", "calls": message['tool_calls']}
        
        # Normal Text Response
        reply = message['content']
        self.memory.add_message("assistant", reply)
        
        # Save interaction to long-term memory
        self.vector_db.store_interaction(prompt, reply)
        
        return {"type": "text", "content": reply}

if __name__ == "__main__":
    brain = LLM()
    print("Brain is ready.")
