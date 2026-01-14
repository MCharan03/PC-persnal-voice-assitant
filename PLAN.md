# Cherry - Sentient OS Layer Roadmap

## Vision
To evolve Cherry into a fully Sentient OS Layer with cognitive persistence, autonomous agency, sensory perception, and emotional intelligence.

## Phase 1: Cognitive Persistence (The Memory Upgrade)
**Goal:** Infinite context and long-term memory.
- [ ] **Vector Database Integration (RAG):** Store interactions, code blocks, and user preferences in a Vector DB (ChromaDB) to answer "Why did my code fail yesterday?".
- [ ] **User Profiling:** Track "Personality Traits" (e.g., preference for brevity) in `user_profile.json` or SQL and dynamically update the System Prompt.

## Phase 2: Autonomous Agency (The "Hands" Upgrade)
**Goal:** Cherry can write its own code, browse the web, and control the computer.
- [ ] **The Agent Loop:** Refactor logic to return Thought/Action/Observation/Final Answer (ReAct pattern).
- [ ] **Tool Construction:**
    - [ ] **Web Scraper:** Playwright/BeautifulSoup.
    - [ ] **File System:** Read/Write permissions with safety checks.
    - [ ] **Calendar/Email:** Google Calendar/Gmail API integration.

## Phase 3: Sensory Perception (The "Senses" Upgrade)
**Goal:** Real-time Voice and Vision (Multimodal).
- [ ] **Real-time Voice:** 
    - [ ] **Input:** Local OpenAI Whisper.
    - [ ] **Output:** ElevenLabs (API) or Coqui TTS (Local).
    - [ ] **Protocol:** WebSockets (`flask-socketio`) for interruptibility.
- [ ] **Vision:** 
    - [ ] Integrate Llava or GPT-4o.
    - [ ] Support screenshot uploads and webcam streaming for error analysis.

## Phase 4: Emotional Intelligence (The "Soul" Upgrade)
**Goal:** Dynamic Personality and Empathy.
- [ ] **Sentiment Analysis Layer:** Fast model (BERT) to detect mood (Frustrated, Happy, Tired) and adjust tone.
- [ ] **Self-Reflection:** Background cron job to review daily logs and summarize learnings to refine future behavior.

## "Iron Man" UI Updates
- [ ] **Audio Visualizer:** Center screen canvas reacting to mic/voice amplitude.
- [ ] **Streaming Text:** Token-by-token text rendering.