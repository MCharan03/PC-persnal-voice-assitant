import os
import subprocess
import datetime
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
from modules.memory_vector import MemoryVector

# Initialize Search Tool
search = DuckDuckGoSearchRun()

# Initialize Memory
# Note: Path is relative to project root usually
memory_vector = MemoryVector(db_path=os.path.join(os.getcwd(), "data", "memory_db"))

@tool
def search_web(query: str) -> str:
    """Useful for searching the internet for current events or facts."""
    try:
        return search.run(query)
    except Exception as e:
        return f"Error searching web: {str(e)}"

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
    Use this when the user explicitly asks to remember something, 
    or shares a personal preference/detail.
    """
    try:
        memory_vector.remember_fact(fact)
        return f"Saved fact: {fact}"
    except Exception as e:
        return f"Error saving memory: {str(e)}"

@tool
def recall_memory(query: str) -> str:
    """
    Searches long-term memory for relevant facts or past conversations.
    Useful when the user refers to past context or asks "Do you remember...?"
    """
    try:
        results = memory_vector.recall(query)
        if results:
            return f"Found memories:\n" + "\n".join(results)
        return "No relevant memories found."
    except Exception as e:
        return f"Error recalling memory: {str(e)}"

# Export list of tools
CHERRY_TOOLS = [search_web, get_current_time, read_local_file, execute_system_command, save_memory, recall_memory]