import os
import subprocess
import datetime
import ollama
from langchain.tools import tool
from duckduckgo_search import DDGS
from modules.memory_vector import MemoryVector
from modules.bridge import server_bridge
from modules.learning import learner

# Custom Search Wrapper
class CustomSearchTool:
    def __init__(self):
        self.ddgs = DDGS()
        
    def run(self, query):
        try:
            results = self.ddgs.text(query, max_results=3)
            if not results:
                return "No results found."
            summary = ""
            for r in results:
                summary += f"- {r['title']}: {r['body']}\n"
            return summary
        except Exception as e:
            return f"Search Error: {str(e)}"

# Initialize Search Tool
search_tool = CustomSearchTool()

# Initialize Memory
db_path = os.path.join(os.getcwd(), "data", "memory_db")
memory_vector = MemoryVector(db_path=db_path)

@tool
def search_web(query: str) -> str:
    """Useful for searching the internet for current events or facts."""
    return search_tool.run(query)

@tool
def get_current_time(query: str = "") -> str:
    """Returns the current local time and date."""
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")

@tool
def read_local_file(file_path: str) -> str:
    """Reads the content of a local file. Provide the full path."""
    try:
        if not os.path.exists(file_path):
            return "File not found."
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def execute_system_command(command: str) -> str:
    """
    Executes a shell command on the user's PC. 
    Use with caution. Useful for opening apps, installing packages, etc.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Command executed. Output: {result.stdout}"
        else:
            return f"Command failed. Error: {result.stderr}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@tool
def save_memory(fact: str) -> str:
    """
    Saves a specific fact to long-term memory. 
    Use this when the user explicitly asks to remember something.
    """
    try:
        memory_vector.remember_fact(fact)
        return f"Saved fact: {fact}"
    except Exception as e:
        return f"Error saving memory: {str(e)}"

@tool
def recall_memory(query: str) -> str:
    """
    Searches long-term memory for relevant facts.
    """
    try:
        results = memory_vector.recall(query)
        if results:
            return f"Found memories:\n" + "\n".join(results)
        return "No relevant memories found."
    except Exception as e:
        return f"Error recalling memory: {str(e)}"

@tool
def see_screen(query: str = "Describe what is on the screen.") -> str:
    """
    Captures the user's screen and analyzes it. 
    Use this when the user says "Look at this", "What's on my screen?", or asks for visual help.
    """
    print(">> [Tool] see_screen called.")
    image_data = server_bridge.request_screenshot()
    if not image_data:
        return "Error: Could not capture screen (Client might be disconnected or timed out)."
    
    print(">> [Tool] Screenshot received. Analyzing with Vision Model...")
    try:
        response = ollama.chat(
            model='llava',
            messages=[{'role': 'user', 'content': query, 'images': [image_data]}]
        )
        return f"Vision Analysis: {response['message']['content']}"
    except Exception as e:
        return f"Vision Error: {str(e)}"

@tool
def learn_new_behavior(instruction: str) -> str:
    """
    Teaches the AI a new rule or correction for future interactions.
    Use this when the user says "Don't do X", "Always do Y", or corrects you.
    Example Input: "When I ask for code, always include comments."
    """
    try:
        learner.add_rule(trigger_context=instruction, rule_instruction=instruction)
        return f"I have learned a new rule: {instruction}"
    except Exception as e:
        return f"Learning Error: {str(e)}"

CHERRY_TOOLS = [search_web, get_current_time, read_local_file, execute_system_command, save_memory, recall_memory, see_screen, learn_new_behavior]