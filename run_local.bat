@echo off
REM Run Mengo-Hub locally on Windows with proper setup
cd /d "%~dp0"

REM Clean pycache to avoid import issues
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
if exist ".pyc" del /s /q ".pyc"

REM Install/update requirements
echo Installing dependencies...
python -m pip install -r requirements.txt

REM Run startup script
echo.
echo Starting Mengo-Hub System...
echo.
python START_SYSTEM.py
