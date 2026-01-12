# Cherry - Unified Personal AI Assistant

Cherry is a fully autonomous, local, and privacy-focused AI assistant inspired by JARVIS. She runs entirely on your PC (Windows) using local LLMs, Vision models, and Vector Databases.

## 🧠 Core Capabilities

*   **Unified Agentic Brain:** Powered by `LangGraph` + `Ollama`. Cherry plans, thinks, and acts.
*   **Multimodal Perception:**
    *   **Hearing:** Real-time Speech-to-Text via `Faster-Whisper` (GPU).
    *   **Sight:** Screen analysis via `Llava` (Vision Model).
    *   **Sensing:** Monitors System Health (CPU/Battery) via `Pulse`.
*   **Emotional Intelligence:** Adapts voice tone and personality based on user sentiment (`TextBlob`).
*   **Self-Learning:** Remembers corrections and learns new behavioral rules permanently (`ChromaDB`).
*   **Tools & Actions:**
    *   Search the Web (`DuckDuckGo`).
    *   Read/Scrape Websites (`BeautifulSoup`).
    *   Control System (Open Apps, Run Commands).
    *   Manage Memory (Save/Recall facts).

## 🚀 Getting Started

### Prerequisites
1.  **Python 3.13** installed.
2.  **Ollama** installed and running.
    *   `ollama pull llama3.2`
    *   `ollama pull llava`
3.  **CUDA Toolkit** (Optional but recommended for fast Whisper STT).

### Installation
1.  Run `setup.bat` (if available) or:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

### Running Cherry
Simply double-click:
**`Start_Cherry.bat`**

## 📂 Architecture

*   **`src/server/`**: The Neural Core (Flask + SocketIO). Handles the Agent, Memory, and Logic.
*   **`src/client/`**: The Interface (PyQt6). Handles Microphone, Wake Word, TTS, and Screen Capture.
*   **`src/modules/`**:
    *   `brain_agent.py`: The LangGraph Agent.
    *   `tools.py`: All available tools (Search, Vision, etc.).
    *   `memory_vector.py`: ChromaDB storage.
    *   `learning.py`: Self-improvement module.
    *   `emotion.py`: Sentiment engine.
    *   `vision.py`: Screenshot handling.

## 🤝 Interaction Examples

*   **"Hey Jarvis, search for the latest tech news."**
*   **"Hey Jarvis, look at this screen and explain the code."**
*   **"Hey Jarvis, remember that I like my coffee black."**
*   **"Hey Jarvis, when I ask for summaries, keep them under 50 words."** (She will learn this rule).

---
*Built with ❤️ using Python, LangChain, and Ollama.*
