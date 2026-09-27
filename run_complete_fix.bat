@echo off
REM Mengo-Hub Complete System Fix & Test
REM Run this script to setup and test everything

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         MENGO-HUB COMPLETE SYSTEM FIX AND TEST                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Clean pycache
echo [1/4] Cleaning pycache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
echo OK
echo.

REM Install/update requirements
echo [2/4] Installing dependencies...
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    exit /b 1
)
echo OK
echo.

REM Run full fix and test
echo [3/4] Running comprehensive checks...
python FULL_FIX_AND_TEST.py
if errorlevel 1 (
    echo ERROR: Fix and test failed
    exit /b 1
)
echo.

REM Start server and then run interactive tests
echo [4/4] Starting server...
echo.
echo The server will start. Once it's running, open another terminal and run:
echo   python INTERACTIVE_TEST.py
echo.
echo Starting server...
python START_SYSTEM.py
