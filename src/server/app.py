import sys
import os
from flask import Flask, request, jsonify

# Add the src directory to sys.path to allow importing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.llm import LLM
from modules.actions import Actions

app = Flask(__name__)
print("--- Initializing Server Core ---")

# Initialize Core Modules
# Note: In a production 'decentralized' setup, these might be singletons or specialized workers
brain = LLM()
hands = Actions()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the health and system stats of the assistant host."""
    stats = hands.get_system_stats()
    return jsonify({
        "status": "online",
        "system_stats": stats
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    The main endpoint for communicating with the assistant remotely.
    Input: JSON { "text": "Open calculator" }
    Output: JSON { "response": "Opening Calculator...", "command": "[OPEN: calculator]" }
    """
    data = request.json
    user_text = data.get('text', '')
    
    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    print(f"[API] User: {user_text}")
    
    # Ask the Brain
    response_text = brain.chat(user_text)
    
    # Process Actions (Server-side execution)
    # If the phone user says "Open Calculator", it opens on the PC (The Server).
    clean_response = handle_server_actions(response_text)
    
    return jsonify({
        "original_response": response_text,
        "clean_response": clean_response
    })

def handle_server_actions(response):
    """
    Executes actions on the HOST machine (the PC running this server).
    """
    import re
    
    # We re-use the logic from main.py but adapted for the API response
    # In a full refactor, this logic should move into modules/actions.py as a static processor
    
    if "[STATS]" in response:
        stats = hands.get_system_stats()
        response = response.replace("[STATS]", "") + f" {stats}"
        
    match = re.search(r"\[OPEN:\s*(.*?)\]", response)
    if match:
        hands.open_app(match.group(1))
        response = response.replace(match.group(0), "")
        
    match = re.search(r"\[SEARCH:\s*(.*?)\]", response)
    if match:
        hands.search_web(match.group(1))
        response = response.replace(match.group(0), "")
        
    match = re.search(r"\[VOLUME:\s*(.*?)\]", response)
    if match:
        hands.adjust_volume(match.group(1))
        response = response.replace(match.group(0), "")
        
    return response.strip()

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible on the local network
    app.run(host='0.0.0.0', port=5000, debug=True)
