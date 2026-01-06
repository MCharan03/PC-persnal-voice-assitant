# Personal AI Voice Assistant Plan

## Project Goal
Build a local, privacy-focused "Jarvis-like" AI assistant for PC without third-party cloud APIs.

## Current Status
- [x] Initial Concept & Stack Proposal
- [x] Architecture Design
- [x] Environment Setup (Python 3.13, PyTorch+CUDA 12.4)
- [x] Core Implementation v1
    - [x] Wake Word Engine (`faster-whisper` tiny model variant / `openWakeWord`)
    - [x] Speech-to-Text (`faster-whisper` small.en on GPU)
    - [x] LLM Integration (`Ollama` / Llama 3.2)
    - [x] Text-to-Speech (`pyttsx3`)
    - [x] System Control Module (App launching, Volume, Search, Stats)
    - [x] UI (PyQt6 Overlay)
- [ ] **Debugging & Optimization (Current Focus)**
    - [x] Fix CUDA/DLL missing errors for `faster-whisper`.
    - [x] Fix Audio Thread Blocking (Refactored to Queue-based system).
    - [ ] **Critical:** Investigate Microphone Input Silence (Software receiving 0.0 amplitude).
- [ ] Future Enhancements
    - [ ] Upgrade TTS to `Kokoro-82M`.
    - [ ] Train custom "Cherry" wake word model.

## Hardware Optimization (Confirmed)
- **CPU:** Intel i7-13650HX
- **GPU:** NVIDIA RTX 4050 (8GB VRAM) -> **Primary driver for STT/LLM via CUDA.**
- **RAM:** 16GB

## Tech Stack (Local Only)

### 1. The "Ears" (Input)
- **Wake Word:** `faster-whisper` (tiny.en) checking buffer / `openWakeWord`.
- **Speech-to-Text (STT):** `Faster-Whisper` (Model: `small.en`)
    - *Optimization:* Run on GPU using `float16` for near-instant transcription.

### 2. The "Brain" (Processing)
- **Engine:** `Ollama`
- **Model:** `Llama-3.2-3B`
    - *Optimization:* Fully offloaded to 8GB VRAM.

### 3. The "Voice" (Output)
- **Text-to-Speech (TTS):** `pyttsx3` (Current), `Kokoro-82M` (Planned).

### 4. The "Hands" (Action)
- **Custom Logic:** Python `subprocess`, `pyautogui`, `psutil`.

### 5. Visual Experience (The "Face")
- **Framework:** `PyQt6`.
- **Design:** Floating cyan orb overlay.