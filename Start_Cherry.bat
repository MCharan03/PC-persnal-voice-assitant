@echo off
echo ===================================================
echo             CHERRY - UNIFIED AI ASSISTANT
echo ===================================================
echo.
echo [1/3] System Checks...
if not exist venv (
    echo Virtual Environment not found! Please run setup first.
    pause
    exit
)
echo.

echo [2/3] Starting Neural Core (Server)...
echo    - Vision System: Online
echo    - Hearing System: Online
echo    - Emotion Engine: Online
echo    - Self-Learning: Online
start "Cherry Brain" /MIN cmd /k "venv\Scripts\python src/server/app.py"

echo.
echo Waiting for Brain to wake up...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Starting Interface (Client)...
start "Cherry Interface" cmd /k "venv\Scripts\python src/client_desktop.py"

echo.
echo System Online.
echo.
echo Available Features:
echo  * Voice Interaction ("Hey Jarvis")
echo  * Screen Vision ("Look at this")
echo  * Web Search & Scraping
echo  * System Control
echo  * Self-Learning ("When I ask X, do Y")
echo.
pause