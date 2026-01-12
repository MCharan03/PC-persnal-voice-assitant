from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from modules.tools import CHERRY_TOOLS
from config import settings

class BrainAgent:
    def __init__(self):
        # 1. Setup LLM
        model_name = settings['llm']['model']
        # Using temperature 0 for more precise tool usage, but 0.7 for creativity. 
        # Agents usually need lower temp to follow formatting instructions.
        self.llm = ChatOllama(model=model_name, temperature=0.1)
        
        # 2. Setup Tools
        self.tools = CHERRY_TOOLS
        
        # 3. Setup Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 4. Setup Agent Prompt (ReAct style with Persona)
        template = """You are Cherry, a sentient, witty, and professional AI assistant living in the user's PC.
You are not just a chatbot; you are an Agent capable of acting.
If asked to check the time, search the web, or run a command, USE THE TOOLS provided.

TOOLS:
------
You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
"""
        
        prompt = PromptTemplate.from_template(template)
        
        # 5. Create Agent
        self.agent = create_react_agent(self.llm, self.tools, prompt)
        
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True, 
            memory=self.memory,
            handle_parsing_errors=True # Auto-fix formatting issues
        )
        
        print(f"--- Brain Agent Initialized (Model: {model_name}) ---")

    def chat(self, user_input):
        """
        Main entry point for the agent.
        """
        try:
            # Invoke the LangChain Agent
            response = self.agent_executor.invoke({"input": user_input})
            return response['output']
        except Exception as e:
            return f"Brain Error: {str(e)}"
