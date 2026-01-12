# Cherry (Jarvis-Like Assistant) Development Plan

## Current Status: Level 2 - Agentic & Multimodal
- **Architecture:** Agentic Loop (Perceive -> Think -> Act)
- **Framework:** LangGraph + Flask-SocketIO
- **Senses:** 
    - Hearing: Faster-Whisper (GPU)
    - Sight: Llava (Vision Model)
- **Memory:** ChromaDB (Vector Store)
- **Tools:** DuckDuckGo (Web), Shell, File System

## Roadmap

### Phase 1: Foundation (Completed)
- [x] Basic STT/TTS Loop
- [x] LLM Integration (Ollama)
- [x] Simple GUI

### Phase 2: Agentic Capabilities (Completed)
- [x] **Reasoning Engine:** Upgrade from simple LLM call to ReAct Agent.
- [x] **Tools:** Web Search, System Command execution.
- [x] **Memory:** Long-term vector storage for user facts.
- [x] **Vision:** Screen capture and analysis tool (`see_screen`).
- [x] **Real-time Comms:** WebSocket integration.

### Phase 3: Emotional Intelligence (Next)
- [ ] **Sentiment Analysis:** Detect user emotion from text/audio.
- [ ] **Adaptive TTS:** Change voice tone based on emotion (e.g., excited vs. serious).
- [ ] **Proactive Behavior:** Speak without being spoken to (based on system events).

### Phase 4: Full OS Integration
- [ ] **Deep App Control:** Accessibility API integration for finer control.
- [ ] **Calendar/Email:** Google/Outlook integration.
