@echo off
echo Starting Cherry Desktop Client...
echo Ensure run_server.bat is running first!
call venv\Scripts\activate
python src\client_desktop.py
pause