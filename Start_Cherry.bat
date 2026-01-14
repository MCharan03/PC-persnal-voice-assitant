@echo off
echo ===================================================
echo   CHERRY - SENTIENT OS LAYER (Monolithic Mode)
echo ===================================================
echo.
echo Initializing Neural Interfaces...
call venv\Scripts\activate

echo Launching Core System (src\main.py)...
python src\main.py
pause
