# SAMBA: Smart Autonomous Machine for Behavioral Assistance 🧠🤖

SAMBA is a modular, local-first, Jarvis-like personal assistant. It combines local LLM reasoning (via Ollama) with system-level execution, memory, and a sleek terminal-style desktop UI.

## 🚀 Features
- **Think-Plan-Execute**: Advanced agentic flow for processing complex requests.
- **Local AI**: Powered by Ollama (Llama 3) for 100% private conversations.
- **Multi-Command Execution**: "Open Chrome and Notepad then run dir".
- **Voice Interface**: Multimodal support with Speech-to-Text and Text-to-Speech.
- **Smart Memory**: Remembers recent context and suggests new workflows based on your behavior.
- **Desktop UI**: A professional, dark-themed Tkinter interface.
- **Safety Shield**: Integrated blocklist to prevent dangerous system commands.

## 🛠️ Project Structure
- `core/`: AI Brain, Intent Parsing, and Decision Engine.
- `executor/`: Secure system execution and safety layers.
- `memory/`: Persistent storage and workflow management.
- `voice/`: Voice input and output modules.
- `ui/`: Desktop GUI.
- `utils/`: Core utilities (logging, state, normalizer).

## 🚦 Quick Start
1. **Prerequisites**: Install [Ollama](https://ollama.com/) and run `ollama pull llama3`.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run CLI**:
   ```bash
   python main.py
   ```
4. **Run Desktop UI**:
   ```bash
   python ui/app.py
   ```

## 🛡️ Safety
SAMBA includes a robust safety layer that prevents execution of harmful commands like `rm -rf` or `format`. All commands are normalized and validated before reaching the system executor.
