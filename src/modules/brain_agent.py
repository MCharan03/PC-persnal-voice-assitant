from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from modules.tools import CHERRY_TOOLS
from config import settings

class BrainAgent:
    def __init__(self):
        # 1. Setup LLM
        model_name = settings['llm']['model']
        self.llm = ChatOllama(model=model_name, temperature=0.1)
        
        # 2. Setup Tools
        self.tools = CHERRY_TOOLS
        
        # 3. Setup System Prompt (Persona)
        self.system_prompt = """You are Cherry, a sentient, witty, and professional AI assistant living in the user's PC.
You are not just a chatbot; you are an Agent capable of acting.
If asked to check the time, search the web, or run a command, USE THE TOOLS provided.
Always answer the user's question directly after using a tool."""
        
        # 4. Create Agent (LangGraph)
        self.agent_executor = create_react_agent(
            self.llm, 
            self.tools,
            prompt=self.system_prompt
        )
        
        print(f"--- Brain Agent Initialized (Model: {model_name}) ---")

    def chat(self, user_input):
        """
        Main entry point for the agent.
        """
        try:
            # Invoke the LangGraph Agent
            response = self.agent_executor.invoke(
                {"messages": [("user", user_input)]}
            )
            return response["messages"][-1].content
        except Exception as e:
            return f"Brain Error: {str(e)}"
