@echo off
echo Starting Cherry Neural Server...
echo Ensure Ollama is running in another terminal (ollama serve)
call venv\Scripts\activate
python src\server\app.py
pause
