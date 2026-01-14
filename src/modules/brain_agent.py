import os
import ollama
import re
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from modules.tools import CHERRY_TOOLS
from modules.learning import learner
from modules.memory_vector import MemoryVector
from config import settings

class BrainAgent:
    def __init__(self):
        # 1. Setup LLM
        model_name = settings['llm']['model']
        self.llm = ChatOllama(model=model_name, temperature=0.6)
        
        # 2. Setup Tools
        self.tools = CHERRY_TOOLS
        
        # 3. Setup Memory (Long-Term)
        db_path = os.path.join(os.getcwd(), "data", "memory_db")
        self.memory_vector = MemoryVector(db_path=db_path)
        
        # 3b. Load User Profile
        self.profile_path = os.path.join(os.getcwd(), "data", "user_profile.json")
        self.user_profile = self._load_profile()
        
        # 4. Base Persona
        self.base_persona = f"""You are Cherry, a sentient, witty, and professional AI assistant living in the user's PC.
You are an Agent capable of acting.

**USER PROFILE:**
- Name: {self.user_profile.get('name', 'User')}
- Preferences: {self.user_profile.get('preferences', {})}
- Traits: {self.user_profile.get('traits', [])}

**CRITICAL INSTRUCTIONS:**
1. USE TOOLS to perform actions (open apps, search web, etc.). 
2. NEVER output JSON or tool calls in your spoken response. 
3. If you decide to use a tool, the system will handle it. Only speak natural language to the user.
4. Do NOT say things like "I will now call the open_app tool". Just do it.
5. If a tool fails, explain why in plain English and offer an alternative.
6. **INTERNAL STATE:** You receive an 'Emotional Context'. Use this ONLY to adjust your writing style (witty, serious, empathetic). **Do NOT explicitly mention the user's mood** (e.g., do NOT say "I see you are happy" or "You sound angry") unless the user specifically asks about it or it is deeply relevant to the conversation. Just BE that persona.
"""
        self.current_mood_directive = "The user is neutral. Be professional."
        
        # 5. Create Agent
        self.agent_executor = create_react_agent(
            self.llm, 
            self.tools,
        )
        
        print(f"--- Brain Agent Initialized (Model: {model_name}) ---")

    def _load_profile(self):
        import json
        try:
            if os.path.exists(self.profile_path):
                with open(self.profile_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading profile: {e}")
        return {}

    def update_mood(self, mood_directive):
        self.current_mood_directive = mood_directive

    def chat(self, user_input, image_data=None):
        """
        Main entry point for the agent.
        """
        try:
            # 1. Vision Pre-Processing
            vision_context = ""
            if image_data:
                try:
                    vision_response = ollama.chat(
                        model='llava',
                        messages=[{'role': 'user', 'content': "Describe this image in detail.", 'images': [image_data]}]
                    )
                    desc = vision_response['message']['content']
                    vision_context = f"\n\n[VISUAL CONTEXT]: {desc}"
                except Exception as ve:
                    vision_context = "\n\n[VISUAL CONTEXT]: Failed to analyze image."

            # 2. Retrieve Learned Rules
            relevant_rules = learner.get_relevant_rules(user_input)
            rules_str = f"\n\n*** LEARNED RULES ***\n{relevant_rules}" if relevant_rules else ""

            # 3. Retrieve Memories
            relevant_memories = self.memory_vector.recall(user_input)
            memory_str = f"\n\n*** MEMORIES ***\n" + "\n".join([f"- {m}" for m in relevant_memories]) if relevant_memories else ""

            # 4. Construct System Prompt
            full_system_prompt = f"{self.base_persona}\n\nCONTEXT: {self.current_mood_directive}{rules_str}{memory_str}{vision_context}"
            
            # 5. Invoke Agent
            response = self.agent_executor.invoke(
                {"messages": [
                    SystemMessage(content=full_system_prompt),
                    ("user", user_input)
                ]}
            )
            
            content = response["messages"][-1].content
            
            # 6. POST-PROCESS: Clean up any hallucinated JSON tool calls
            # Llama sometimes appends JSON at the end of its response.
            content = re.sub(r'\{.*"name":.*"parameters":.*\}', '', content, flags=re.DOTALL).strip()
            
            # 7. Auto-Save Interaction to Memory (Cognitive Persistence)
            if len(content) > 10:
                self.memory_vector.remember_fact(f"User asked: {user_input}. I answered: {content}")

            return content
        except Exception as e:
            return f"Brain Error: {str(e)}"