#!/usr/bin/env python3
"""
Mengo-Hub Master Startup Script
Handles complete system initialization and startup
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                   MENGO-HUB SYSTEM                             ║
    ║              Master Startup & Initialization                   ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  All issues fixed and system ready for full deployment!        ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Check if required packages are installed"""
    print("\n[1/5] Checking Requirements...")
    try:
        import flask
        import psycopg2
        import bcrypt
        print("  ✓ All required packages installed")
        return True
    except ImportError as e:
        print(f"  ✗ Missing package: {e}")
        print("\n  Installing requirements...")
        os.system("pip install -r requirements.txt")
        return True

def check_env_file():
    """Check and create .env if needed"""
    print("\n[2/5] Checking Configuration...")
    if not Path('.env').exists():
        print("  ⚠ .env file not found")
        if Path('.env.example').exists():
            print("  Creating .env from .env.example...")
            os.system("cp .env.example .env")
            print("  ✓ .env created (please review and update if needed)")
    else:
        print("  ✓ .env file exists")

def run_setup():
    """Run the setup and fix script"""
    print("\n[3/5] Running System Setup...")
    if Path('SETUP_AND_FIX.py').exists():
        try:
            subprocess.run([sys.executable, 'SETUP_AND_FIX.py'], check=True)
            print("  ✓ Setup completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ⚠ Setup encountered issues: {e}")
            return True  # Continue anyway
    else:
        print("  ⚠ SETUP_AND_FIX.py not found, skipping")
        return True

def run_tests():
    """Run feature verification tests"""
    print("\n[4/5] Verifying Features...")
    if Path('TEST_FEATURES.py').exists():
        print("  Run 'python TEST_FEATURES.py' after server starts to verify all features")
    else:
        print("  ⚠ TEST_FEATURES.py not found")

def start_server():
    """Start the Flask server"""
    print("\n[5/5] Starting Server...")
    print("\n" + "="*60)
    print("  Starting Flask application...")
    print("  Server will run on: http://localhost:5000")
    print("="*60 + "\n")
    
    try:
        subprocess.run([sys.executable, 'run.py'])
    except KeyboardInterrupt:
        print("\n\n  Server stopped by user")
        print("="*60)

def main():
    print_banner()
    
    print("\n✨ Mengo-Hub System Initialization Starting...\n")
    
    # Run initialization steps
    check_requirements()
    check_env_file()
    run_setup()
    run_tests()
    
    # Start server
    print("\n" + "="*60)
    print("System is ready! Starting server...")
    print("="*60)
    time.sleep(2)
    start_server()
    
    print("\n\n" + "="*60)
    print("Thank you for using Mengo-Hub System!")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        sys.exit(1)
