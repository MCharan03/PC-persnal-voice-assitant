# Cherry 🍒 - Personal AI Desktop Assistant

**Cherry** is a privacy-focused, fully local AI voice assistant for Windows. Designed to act like a "Jarvis" for your PC, she lives in the background, wakes up when called, and can control your computer, answer questions, and assist with tasks—all without sending a single byte of data to the cloud.

## 🚀 Key Features

*   **100% Offline & Private:** Uses local models for hearing, thinking, and speaking.
*   **Wake Word Activation:** Listens efficiently in the background for "Hey Jarvis" (Customizable).
*   **Natural Conversation:** Powered by **Llama 3.2** (via Ollama) for intelligent, context-aware responses.
*   **Lightning Fast:** Optimized for NVIDIA GPUs (CUDA) using `Faster-Whisper` and `PyTorch`.
*   **Futuristic UI:** A transparent, pulsing desktop overlay that appears only when you need it.
*   **PC Control & Automation:**
    *   Open Applications (Chrome, VS Code, etc.)
    *   Adjust Volume
    *   Check System Stats (CPU, RAM, Battery)
    *   Perform Web Searches
*   **Remote Server API:** Control your PC from other devices via the Flask server.

## 🛠️ Tech Stack

- **Language:** Python 3.13
- **Speech-to-Text (STT):** `Faster-Whisper` (running on CUDA)
- **Large Language Model (LLM):** `Ollama` (Llama 3.2 3B)
- **Text-to-Speech (TTS):** `Kokoro` (High Quality) / `pyttsx3` (Fallback)
- **Wake Word:** `openWakeWord`
- **GUI:** `PyQt6`
- **Server:** `Flask`
- **Automation:** `pyautogui`, `psutil`, `subprocess`

## 📦 Installation & Setup

### Prerequisites
1.  **NVIDIA GPU** (Recommended for speed).
2.  **Ollama** installed and running ([Download here](https://ollama.com)).
3.  **Python 3.10+**.

### Setup Steps
1.  Clone the project.
2.  Download the AI model:
    ```bash
    ollama pull llama3.2
    ```
3.  Create a virtual environment and install dependencies:
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```
    *(Note: Ensure PyTorch is installed with CUDA support)*

4.  **Configuration:**
    Check `config/settings.yaml` to adjust VAD sensitivity, models, or wake words.

5.  Run Cherry:
    ```powershell
    python src/main.py
    ```

## 🎮 Usage

### Desktop Mode
1.  Run `src/main.py`. Cherry will start silently in the background.
2.  Say **"Hey Jarvis"**.
3.  A cyan orb will appear on your screen. Speak your command.

### Server Mode (Mobile Support)
Run the server to accept remote commands:
```powershell
python src/server/app.py
```
*   **Endpoint:** `http://YOUR_PC_IP:5000/api/voice` (POST .wav file)
*   **Endpoint:** `http://YOUR_PC_IP:5000/api/chat` (POST JSON `{"text": "..."}`)

This allows you to control your PC (e.g., "Volume Up", "Open Steam") from a mobile app connected to the same network.

## 🗓️ Project Roadmap

- [x] **Phase 1: Core System** (STT, LLM, Basic TTS, Wake Word) - *Completed*
- [x] **Phase 2: Visual Interface** (PyQt6 Overlay) - *Completed*
- [x] **Phase 3: PC Control** (App launching, System stats) - *Completed*
- [x] **Phase 4: Server API** (Remote control) - *Completed*
- [ ] **Phase 5: Custom Wake Word** (Train "Hey Cherry" model)
- [ ] **Phase 6: Memory** (Remember user preferences across sessions)

## 📂 Directory Structure

```
E:\personal voice assitant\
├── assets/              # Models and Icons
├── config/              # Configuration (settings.yaml)
├── scripts/             # Helper scripts and tests
├── src/
│   ├── modules/
│   │   ├── actions.py           # PC Control Logic
│   │   ├── command_processor.py # Central Command Parser
│   │   ├── llm.py               # Ollama Integration
│   │   ├── stt.py               # Whisper Speech Recognition
│   │   ├── tts.py               # Text-to-Speech
│   │   ├── vad.py               # Voice Activity Detection
│   │   └── wake_word.py         # Wake Word Engine
│   ├── server/
│   │   └── app.py               # Flask Server
│   ├── gui.py                   # Visual Overlay (PyQt6)
│   ├── main.py                  # Core Application Loop
│   └── config.py                # Configuration Loader
└── venv/                        # Python Virtual Environment
```