@echo off
echo ===================================================
echo   CHERRY - SENTIENT OS LAYER (LEVEL 2)
echo ===================================================
echo.
echo [1/3] Checks...
if not exist venv (
    echo Virtual Environment not found! Please run setup first.
    pause
    exit
)
echo.

echo [2/3] Starting Neural Core (Server)...
start "Cherry Brain" /MIN cmd /k "venv\Scripts\python src/server/app.py"

echo.
echo Waiting for Brain to wake up...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Starting Interface (Client)...
start "Cherry Interface" cmd /k "venv\Scripts\python src/client_desktop.py"

echo.
echo System Online.
echo Say "Hey Jarvis" to begin.
echo.
pause
