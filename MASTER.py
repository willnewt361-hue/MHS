#!/usr/bin/env python3
"""
Mengo-Hub Master Control Center
Central hub for all operations: setup, testing, troubleshooting
"""

import os
import sys
import subprocess
from pathlib import Path

def clear_screen():
    """Clear screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print main banner"""
    clear_screen()
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║         🎓 MENGO-HUB SYSTEM - MASTER CONTROL CENTER           ║
    ║                                                                ║
    ║             Complete Learning Management System                ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

def show_main_menu():
    """Show main menu"""
    print("""
    ┌─ MAIN MENU ───────────────────────────────────────────────────┐
    │                                                               │
    │  [1] ✅ Quick Setup & Start                                   │
    │      Run all fixes and start the system                        │
    │                                                                │
    │  [2] 🔍 Verify & Diagnose                                     │
    │      Run comprehensive system checks                           │
    │                                                                │
    │  [3] 🧪 Run Tests                                             │
    │      Test all endpoints and functionality                      │
    │                                                                │
    │  [4] 📖 View Documentation                                    │
    │      Show guides and troubleshooting                           │
    │                                                                │
    │  [5] 🚀 Start Server Only                                     │
    │      Start Flask server (for manual testing)                   │
    │                                                                │
    │  [6] 🔧 Advanced Tools                                        │
    │      Troubleshoot and debug tools                              │
    │                                                                │
    │  [0] ❌ Exit                                                   │
    │                                                                │
    └────────────────────────────────────────────────────────────────┘
    """)

def option_quick_setup():
    """Quick setup and start"""
    clear_screen()
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║              [1] QUICK SETUP & START                           ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n⏳ Running setup procedures...\n")
    
    steps = [
        ("Cleaning cache", "for /d /r . %d in (__pycache__) do @if exist \"%d\" rd /s /q \"%d\"" if os.name == 'nt' else "find . -type d -name __pycache__ -exec rm -rf {} +"),
        ("Installing dependencies", f"{sys.executable} -m pip install -r requirements.txt -q"),
        ("Running diagnostics", f"{sys.executable} FULL_FIX_AND_TEST.py"),
    ]
    
    for step_name, cmd in steps:
        print(f"  ⏳ {step_name}...")
        try:
            if os.name == 'nt':
                result = os.system(cmd)
            else:
                result = os.system(cmd)
            
            if result == 0 or step_name == "Cleaning cache":
                print(f"  ✅ {step_name} completed")
            else:
                print(f"  ⚠️  {step_name} encountered issues")
        except Exception as e:
            print(f"  ❌ {step_name} failed: {e}")
    
    print("\n" + "="*60)
    print("Starting server...")
    print("="*60)
    print("\nServer starting on http://localhost:5000")
    print("\nTo test endpoints, open another terminal and run:")
    print("  python MASTER.py")
    print("  Then select option [3] to run tests\n")
    print("="*60)
    
    os.system(f"{sys.executable} START_SYSTEM.py")

def option_verify():
    """Verify and diagnose"""
    clear_screen()
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║              [2] VERIFY & DIAGNOSE                             ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n🔍 Running comprehensive system checks...\n")
    os.system(f"{sys.executable} FULL_FIX_AND_TEST.py")
    
    input("\n\nPress Enter to return to menu...")

def option_run_tests():
    """Run tests"""
    clear_screen()
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║              [3] RUN TESTS                                     ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n🧪 Running interactive tests...\n")
    print("Make sure the server is running (option [5])!")
    print("You can run this in a separate terminal.\n")
    
    os.system(f"{sys.executable} INTERACTIVE_TEST.py")
    
    input("\n\nPress Enter to return to menu...")

def option_view_docs():
    """View documentation"""
    clear_screen()
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║              [4] VIEW DOCUMENTATION                            ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    docs_menu = """
    ┌─ DOCUMENTATION ───────────────────────────────────────────────┐
    │                                                                │
    │  [a] COMPLETE_GUIDE.md      - Full setup and troubleshooting  │
    │  [b] SYSTEM_STATUS.md       - What was fixed and how          │
    │  [c] README_FIRST.md        - Getting started guide           │
    │  [d] Test Credentials       - Show login credentials          │
    │                                                               │
    │  [0] Back to main menu                                        │
    │                                                                │
    └────────────────────────────────────────────────────────────────┘
    """
    
    while True:
        print(docs_menu)
        choice = input("Select: ").strip().lower()
        
        if choice == 'a':
            os.system('type COMPLETE_GUIDE.md' if os.name == 'nt' else 'cat COMPLETE_GUIDE.md')
        elif choice == 'b':
            os.system('type SYSTEM_STATUS.md' if os.name == 'nt' else 'cat SYSTEM_STATUS.md')
        elif choice == 'c':
            os.system('type README_FIRST.md' if os.name == 'nt' else 'cat README_FIRST.md')
        elif choice == 'd':
            print("""
    ┌─ TEST CREDENTIALS ────────────────────────────────────────────┐
    │                                                               │
    │  ADMIN (Super User - A000):                                   │
    │    Username: Newton                                           │
    │    Password: ##0000                                           │
    │    Note: Not logged in audit logs ✓                           │
    │                                                               │
    │  CSV STUDENTS:                                                │
    │    jdoe / password123                                         │
    │    asmith / password123                                       │
    │    bwilson / password123                                      │
    │                                                               │
    │  CSV TEACHERS:                                                │
    │    jane_smith / password123                                   │
    │    mike_jones / password123                                   │
    │    sarah_lee / password123                                    │
    │                                                               │
    │  CSV IMPORT PASSWORD:                                         │
    │    ImportPassword2026                                         │
    │                                                                │
    └────────────────────────────────────────────────────────────────┘
            """)
        elif choice == '0':
            break
        
        input("\nPress Enter to continue...")
        clear_screen()

def option_start_server():
    """Start server only"""
    clear_screen()
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║              [5] START SERVER ONLY                             ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n🚀 Starting server...\n")
    print("Server will run on: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    print("="*60)
    
    os.system(f"{sys.executable} run.py")

def option_advanced():
    """Advanced tools"""
    clear_screen()
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║              [6] ADVANCED TOOLS                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    advanced_menu = """
    ┌─ ADVANCED TOOLS ──────────────────────────────────────────────┐
    │                                                                │
    │  [a] Clean Python Cache                                       │
    │      Remove all __pycache__ directories                       │
    │                                                                │
    │  [b] Reinstall Dependencies                                   │
    │      Force reinstall all packages                             │
    │                                                                │
    │  [c] Database Diagnostics                                     │
    │      Check database connections and tables                    │
    │                                                                │
    │  [d] Test Specific Endpoint                                   │
    │      Make direct HTTP calls to endpoints                      │
    │                                                                │
    │  [0] Back to main menu                                        │
    │                                                                │
    └────────────────────────────────────────────────────────────────┘
    """
    
    while True:
        print(advanced_menu)
        choice = input("Select: ").strip().lower()
        
        if choice == 'a':
            print("\n🧹 Cleaning Python cache...")
            if os.name == 'nt':
                os.system('for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"')
            else:
                os.system('find . -type d -name __pycache__ -exec rm -rf {} +')
            print("✅ Cache cleaned")
        
        elif choice == 'b':
            print("\n📦 Reinstalling dependencies...")
            os.system(f"{sys.executable} -m pip install --upgrade -r requirements.txt")
            print("✅ Dependencies updated")
        
        elif choice == 'c':
            print("\n🔍 Database Diagnostics...")
            # Simple database test
            try:
                import psycopg2
                from dotenv import load_dotenv
                load_dotenv()
                
                db_url = os.getenv('DATABASE_URL')
                print(f"Database URL: {db_url}")
                
                conn = psycopg2.connect(db_url)
                print("✅ PostgreSQL connection successful")
                conn.close()
            except Exception as e:
                print(f"❌ Database error: {e}")
        
        elif choice == 'd':
            endpoint = input("\nEnter endpoint (e.g., /api/status): ").strip()
            try:
                import requests
                response = requests.get(f"http://localhost:5000{endpoint}", timeout=3)
                print(f"\nStatus: {response.status_code}")
                print(f"Response:\n{response.json()}")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '0':
            break
        
        input("\nPress Enter to continue...")
        clear_screen()

def main():
    """Main menu loop"""
    while True:
        print_banner()
        show_main_menu()
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            option_quick_setup()
        elif choice == '2':
            option_verify()
        elif choice == '3':
            option_run_tests()
        elif choice == '4':
            option_view_docs()
        elif choice == '5':
            option_start_server()
        elif choice == '6':
            option_advanced()
        elif choice == '0':
            print("\n👋 Thank you for using Mengo-Hub!\n")
            sys.exit(0)
        else:
            print("❌ Invalid option")
            input("Press Enter to continue...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
