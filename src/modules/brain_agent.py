from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from modules.tools import CHERRY_TOOLS
from modules.learning import learner
from config import settings

class BrainAgent:
    def __init__(self):
        # 1. Setup LLM
        model_name = settings['llm']['model']
        self.llm = ChatOllama(model=model_name, temperature=0.6)
        
        # 2. Setup Tools
        self.tools = CHERRY_TOOLS
        
        # 3. Base Persona
        self.base_persona = """You are Cherry, a sentient, witty, and professional AI assistant living in the user's PC.
You are not just a chatbot; you are an Agent capable of acting.
If asked to check the time, search the web, or run a command, USE THE TOOLS provided.
Always answer the user's question directly after using a tool.
"""
        self.current_mood_directive = "The user is neutral. Be professional."
        
        # 4. Create Agent
        self.agent_executor = create_react_agent(
            self.llm, 
            self.tools,
        )
        
        print(f"--- Brain Agent Initialized (Model: {model_name}) ---")

    def update_mood(self, mood_directive):
        self.current_mood_directive = mood_directive

    def chat(self, user_input):
        """
        Main entry point for the agent.
        """
        try:
            # 1. Retrieve Learned Rules (Self-Correction)
            relevant_rules = learner.get_relevant_rules(user_input)
            rules_str = ""
            if relevant_rules:
                rules_str = f"\n\n*** IMPORTANT LEARNED RULES ***\n{relevant_rules}\n******************************"

            # 2. Construct Dynamic System Prompt
            full_system_prompt = f"{self.base_persona}\n\nCURRENT EMOTIONAL CONTEXT: {self.current_mood_directive}{rules_str}"
            
            # 3. Invoke Agent
            response = self.agent_executor.invoke(
                {"messages": [
                    SystemMessage(content=full_system_prompt),
                    ("user", user_input)
                ]}
            )
            return response["messages"][-1].content
        except Exception as e:
            return f"Brain Error: {str(e)}"
