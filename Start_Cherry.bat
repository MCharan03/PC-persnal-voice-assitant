@echo off
title Cherry Launcher
color 0b

:MENU
cls
echo ===================================================
echo   CHERRY - SENTIENT OS LAYER
echo ===================================================
echo.
echo  [1] Start Cherry Server (New "Iron Man" Web UI)
echo      - Best for Phase 2 & 3 (Agent + Visualizer)
echo      - Access at http://localhost:5001
echo.
echo  [2] Start Cherry Desktop (Legacy Monolithic)
echo      - PyQt Window, runs everything in one process.
echo.
echo  [3] Exit
echo.
set /p choice="Select Mode (1-3): "

if "%choice%"=="1" goto SERVER
if "%choice%"=="2" goto DESKTOP
if "%choice%"=="3" goto EOF

:SERVER
cls
echo Initializing Cherry Neural Server...
call venv\Scripts\activate
start http://localhost:5001
python src\server\app.py
pause
goto EOF

:DESKTOP
cls
echo Launching Core System...
call venv\Scripts\activate
python src\main.py
pause
goto EOF

:EOF
exit