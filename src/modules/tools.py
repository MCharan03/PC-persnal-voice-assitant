import os
import subprocess
import datetime
import ollama
import pyautogui
import win32gui
import win32process
import psutil
import webbrowser
from langchain.tools import tool
from duckduckgo_search import DDGS
from modules.memory_vector import MemoryVector
from modules.bridge import server_bridge
from modules.learning import learner
from modules.web_scraper import scrape_website
from modules.agency import cherry_agency

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
                summary += f"- {r['title']} ({r['href']}): {r['body']}\n"
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
def deep_research(query: str) -> str:
    """
    Performs a deep research by searching the web and then reading the content of the top result.
    Use this for complex questions requiring detailed answers.
    """
    try:
        results = search_tool.ddgs.text(query, max_results=1)
        if not results: return "Research failed: No results."
        first_result = results[0]
        content = scrape_website.invoke(first_result['href'])
        return f"Research on '{first_result['title']}':\n{content[:2000]}..."
    except Exception as e:
        return f"Deep Research Error: {str(e)}"

@tool
def open_application(target: str) -> str:
    """
    Finds and opens a desktop application or file on the user's PC.
    Target can be an app name (e.g., 'chrome', 'notepad') or a file path.
    """
    import os
    import platform
    import subprocess
    
    try:
        if platform.system() == "Windows":
            # os.startfile is "magic" on Windows - it opens apps, files, folders, URLs
            os.startfile(target)
            return f"Opening '{target}' via system start..."
        elif platform.system() == "Darwin": # Mac
            subprocess.call(["open", target])
            return f"Opening '{target}' via Mac open..."
        else: # Linux
            subprocess.call(["xdg-open", target])
            return f"Opening '{target}' via xdg-open..."
    except Exception as e:
        # Fallback for app names that aren't paths
        try:
            if platform.system() == "Windows":
                subprocess.Popen(f"start {target}", shell=True)
                return f"Invoked 'start' for '{target}'."
        except:
            pass
        return f"Error opening '{target}': {str(e)}"

@tool
def read_local_file(file_path: str) -> str:
    """Reads the content of a local file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f: 
            return f.read()
    except Exception as e: 
        return f"Error reading file: {str(e)}"

@tool
def write_local_file(file_path: str, content: str) -> str:
    """Creates or updates a local file with the provided content."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote content to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def system_control(action: str, value: str = "") -> str:
    """
    Controls system settings like volume, media, or windows.
    Actions: 'volume_up', 'volume_down', 'mute', 'play_pause', 'next_track', 'minimize_all'.
    """
    try:
        if action == "volume_up":
            for _ in range(5): pyautogui.press('volumeup')
            return "Volume increased."
        elif action == "volume_down":
            for _ in range(5): pyautogui.press('volumedown')
            return "Volume decreased."
        elif action == "mute":
            pyautogui.press('volumemute')
            return "Volume muted/unmuted."
        elif action == "play_pause":
            pyautogui.press('playpause')
            return "Toggled media playback."
        elif action == "next_track":
            pyautogui.press('nexttrack')
            return "Skipped to next track."
        elif action == "minimize_all":
            pyautogui.hotkey('win', 'd')
            return "Minimized all windows."
        return "Unknown system action."
    except Exception as e:
        return f"System Control Error: {e}"

@tool
def set_background_goal(goal_description: str, detailed_instruction: str) -> str:
    """
    Spawns a background task for Cherry to work on while the user does other things.
    """
    task_id = cherry_agency.add_task(
        description=goal_description,
        func=deep_research.invoke,
        args={"query": detailed_instruction}
    )
    return f"I've started working on '{goal_description}' in the background. (Task ID: {task_id})."

@tool
def check_background_tasks(query: str = "") -> str:
    """Returns a report of background tasks."""
    return cherry_agency.get_status_report()

@tool
def get_active_window_context(query: str = "") -> str:
    """Returns info about the focused window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid).name()
        return f"Active Window: '{title}' (Process: {process})"
    except Exception as e:
        return f"Error: {e}"

@tool
def control_pc_ui(action: str, target: str = "") -> str:
    """Controls the PC UI (click, type, press)."""
    try:
        if action == "type":
            pyautogui.write(target, interval=0.05)
            return f"Typed: {target}"
        elif action == "press":
            pyautogui.press(target)
            return f"Pressed key: {target}"
        elif action == "click":
            pyautogui.click()
            return "Clicked."
        return "Unknown action."
    except Exception as e:
        return f"Error: {e}"

@tool
def get_current_time(query: str = "") -> str:
    """Returns the current time."""
    return datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

@tool
def read_local_file(file_path: str) -> str:
    """Reads a local file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e: return f"Error: {str(e)}"

@tool
def execute_system_command(command: str) -> str:
    """Executes a shell command. Use with extreme caution."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"Out: {result.stdout}\nErr: {result.stderr}"
    except Exception as e: return f"Error: {str(e)}"

@tool
def save_memory(fact: str) -> str:
    """Saves a fact to long-term memory."""
    memory_vector.remember_fact(fact)
    return f"Saved: {fact}"

@tool
def recall_memory(query: str) -> str:
    """Recalls facts from memory."""
    results = memory_vector.recall(query)
    return f"Found:\n" + "\n".join(results) if results else "No memories found."

@tool
def see_screen(query: str = "Describe the screen.") -> str:
    """Captures and analyzes the screen."""
    try:
        from PIL import ImageGrab
        import io
        screenshot = ImageGrab.grab()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='JPEG', quality=80)
        image_data = img_byte_arr.getvalue()
        response = ollama.chat(model='llava', messages=[{'role': 'user', 'content': query, 'images': [image_data]}])
        return f"Vision: {response['message']['content']}"
    except Exception as e: return f"Error: {str(e)}"

CHERRY_TOOLS = [
    search_web, deep_research, open_application, system_control,
    set_background_goal, check_background_tasks,
    get_active_window_context, control_pc_ui, get_current_time, 
    read_local_file, write_local_file, execute_system_command, 
    save_memory, recall_memory, see_screen, scrape_website
]
