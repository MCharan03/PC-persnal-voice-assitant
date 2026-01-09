@echo off
echo Initializing Cherry AI Core...
call venv\Scripts\activate

REM Check if Ollama is accessible
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] 'ollama' command not found!
    echo Please install Ollama from https://ollama.com/download/windows
    echo After installing, open a new terminal and run: ollama pull llama3.2
    echo.
    pause
    exit
)

start /B pythonw src/boot.py
exit
