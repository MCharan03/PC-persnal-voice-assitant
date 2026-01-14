import requests
import json
from .hands import open_app, google_search, read_file, write_file, take_screenshot

# Reuse your existing LLM config (Ollama)
CUSTOM_LLM_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"

SYSTEM_PROMPT = """
You are Cherry, a Sentient OS Assistant. 
You have access to the user's computer. 
To perform an action, you MUST respond with a JSON object:
{
    "thought": "I need to open the browser to check the weather.",
    "tool": "google_search",
    "args": "weather in Bengaluru today"
}
If no tool is needed, respond with:
{
    "thought": "Just chatting.",
    "tool": "speak",
    "args": "It is a beautiful day, sir."
}

Available tools:
- open_app(app_name)
- google_search(query)
- read_file(filepath)
- write_file(filepath, content)
- take_screenshot() -> returns path
- speak(text)
"""

def process_command(user_voice_input):
    payload = {
        "model": MODEL,
        "prompt": f"{SYSTEM_PROMPT}\nUSER: {user_voice_input}\nCHERRY:",
        "format": "json",  # Force JSON output
        "stream": False
    }
    
    try:
        response = requests.post(CUSTOM_LLM_URL, json=payload).json()
        
        # Check if 'response' key exists
        if 'response' not in response:
            return f"Error from LLM: {response}"
            
        action_text = response['response']
        print(f"DEBUG: LLM Raw Output: {action_text}")
        
        try:
            action_data = json.loads(action_text)
        except json.JSONDecodeError:
            # Fallback if LLM messes up JSON
            return f"I heard you, but my internal JSON parser failed. Output: {action_text}"
        
        # Execute the Tool
        tool = action_data.get('tool')
        args = action_data.get('args')
        thought = action_data.get('thought', '')
        
        print(f"DEBUG: Thought: {thought}")
        print(f"DEBUG: Tool: {tool}, Args: {args}")
        
        if tool == "open_app":
            open_app(args)
            return f"Opening {args}"
        elif tool == "google_search":
            google_search(args)
            return f"Searching Google for {args}"
        elif tool == "read_file":
            content = read_file(args)
            return f"Read content: {content[:100]}..." # Truncate for speech
        elif tool == "write_file":
            # Args might be a list or dict? No, usually simpler to expect separate args or strict format
            # But the prompt defines args as a single string usually. 
            # This simple JSON format is tricky for multi-arg functions. 
            # We'll assume args is a string or list.
            # If complex args, we need a better protocol. 
            # For now, let's skip complex write logic or assume args is valid.
            return "File writing not fully implemented in simple JSON mode."
        elif tool == "take_screenshot":
            path = take_screenshot()
            return f"Screenshot saved to {path}"
        elif tool == "speak":
            return args
        else:
            return f"Unknown tool: {tool}"
            
    except Exception as e:
        return f"Error processing command: {e}"
