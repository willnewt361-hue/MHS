@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo Mengo-Hub System - Local HTTPS Setup
echo ===============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo [OK] Python found

REM Check OpenSSL
openssl version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] OpenSSL not found. Installing via Win32 OpenSSL...
    echo Visit: https://slproweb.com/products/Win32OpenSSL.html
    echo Please install and add to PATH, then run this script again
    pause
    exit /b 1
)
echo [OK] OpenSSL found

REM Generate certificates if they don't exist
if not exist "cert.pem" (
    echo.
    echo [*] Generating self-signed SSL certificate...
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 ^
      -subj "/C=UG/ST=Kampala/L=Kampala/O=Mengo/CN=localhost"
    
    if errorlevel 1 (
        echo [ERROR] Failed to generate certificates
        pause
        exit /b 1
    )
    echo [OK] Certificate generated: cert.pem, key.pem
)

REM Install/update dependencies
echo.
echo [*] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Create .env if it doesn't exist
if not exist ".env" (
    echo.
    echo [*] Creating .env file with defaults...
    (
        echo DATABASE_TYPE=postgresql
        echo DATABASE_URL=postgresql://postgres:##000000@localhost:5432/mengo_hub
        echo FLASK_ENV=development
        echo FLASK_DEBUG=True
        echo SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%
        echo EMAIL_PROVIDER=gmail
        echo EMAIL_SENDER=noreply@mengo-hub.com
        echo EMAIL_SENDER_NAME=Mengo-Hub System
    ) > .env
    echo [OK] .env created - update with your settings
)

REM Clear screen and display info
cls
echo.
echo ===============================================
echo       Mengo-Hub - Local HTTPS Server
echo ===============================================
echo.
echo [✓] Setup complete!
echo.
echo Access Mengo-Hub at:
echo   https://localhost:5000/
echo.
echo Default Credentials:
echo   Username: admin
echo   Password: ##0000
echo.
echo IMPORTANT:
echo   1. You'll see an SSL certificate warning - this is NORMAL
echo   2. Click "Advanced" and "Proceed to localhost"
echo   3. This is only for local development
echo.
echo Press any key to start the server...
pause >nul

REM Start Flask app
echo.
echo [*] Starting Mengo-Hub server...
echo [*] Initializing database...
echo.
python flask_app.py

pause
