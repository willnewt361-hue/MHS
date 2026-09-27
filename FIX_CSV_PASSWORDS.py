#!/usr/bin/env python3
"""
CSV User Password Fixer
Re-hashes and fixes CSV imported user passwords if needed
"""

import bcrypt
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'postgresql').lower()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:##0000@localhost:5432/mengo_hub')

def get_db_connection():
    """Get database connection"""
    if DATABASE_TYPE == 'postgresql':
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    else:
        import sqlite3
        db_path = DATABASE_URL if DATABASE_URL else 'data/mengo.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def fix_csv_passwords():
    """Fix CSV imported user passwords"""
    print("\n[1] Scanning CSV users for unhashed passwords...")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # CSV users we know about
        csv_usernames = [
            'jdoe', 'asmith', 'bwilson', 'elyon256', 'joshua123', 'luboyera1', 
            'busuulwa1', 'musisi1', 'nsubuga1', 'sempa1', 'armitage1', 'kennedy1',
            'george1', 'ezer123', 'Pretty-Kats', 'Kraazyy-xta', 'lastsavage 84',
            'its-mj-33', 'cyb.n.ivy', 'Beloved', 'eron-ayaan44', 'Will_newton',
            'jane_smith', 'mike_jones', 'sarah_lee', 'daniel_kamanzi'
        ]
        
        # CSV test credential
        known_passwords = {
            'jdoe': 'password123',
            'asmith': 'password123',
            'bwilson': 'password123',
            'elyon256': 'Zunknown8',
            'joshua123': 'bzorp12',
            'Will_newton': '##silence',
            'jane_smith': 'password123',
            'mike_jones': 'password123',
            'sarah_lee': 'password123',
            'daniel_kamanzi': 'password123',
        }
        
        users_to_fix = []
        
        # Check students
        if DATABASE_TYPE == 'postgresql':
            for username in csv_usernames:
                cur.execute("""
                    SELECT id, username, password FROM students WHERE username = %s
                """, (username,))
                user = cur.fetchone()
                
                if user:
                    user_id, db_username, db_password = user
                    
                    # Check if password is NOT a bcrypt hash
                    if db_password and not db_password.startswith('$2'):
                        users_to_fix.append({
                            'table': 'students',
                            'id': user_id,
                            'username': db_username,
                            'current_password': db_password,
                            'should_be': known_passwords.get(db_username, db_password)
                        })
                        print(f"  Found unhashed password: {db_username} (ID: {user_id})")
        else:
            for username in csv_usernames:
                cur.execute("""
                    SELECT id, username, password FROM students WHERE username = ?
                """, (username,))
                user = cur.fetchone()
                
                if user:
                    user_id = user['id']
                    db_username = user['username']
                    db_password = user['password']
                    
                    # Check if password is NOT a bcrypt hash
                    if db_password and not db_password.startswith('$2'):
                        users_to_fix.append({
                            'table': 'students',
                            'id': user_id,
                            'username': db_username,
                            'current_password': db_password,
                            'should_be': known_passwords.get(db_username, db_password)
                        })
                        print(f"  Found unhashed password: {db_username} (ID: {user_id})")
        
        if not users_to_fix:
            print("  ✓ No unhashed passwords found!")
            conn.close()
            return True
        
        print(f"\n  Found {len(users_to_fix)} users with unhashed passwords")
        
        # Fix them
        print(f"\n[2] Hashing {len(users_to_fix)} passwords...")
        
        fixed_count = 0
        for user in users_to_fix:
            try:
                # Get the password to hash
                password_to_hash = user['should_be']
                hashed = hash_password(password_to_hash)
                
                # Update database
                if DATABASE_TYPE == 'postgresql':
                    cur.execute("""
                        UPDATE students SET password = %s WHERE id = %s
                    """, (hashed, user['id']))
                else:
                    cur.execute("""
                        UPDATE students SET password = ? WHERE id = ?
                    """, (hashed, user['id']))
                
                print(f"  ✓ Fixed: {user['username']}")
                fixed_count += 1
            except Exception as e:
                print(f"  ✗ Error fixing {user['username']}: {e}")
        
        conn.commit()
        print(f"\n[3] Verification...")
        
        # Verify fix
        for user in users_to_fix[:3]:  # Verify first 3
            if DATABASE_TYPE == 'postgresql':
                cur.execute("""
                    SELECT password FROM students WHERE id = %s
                """, (user['id'],))
                result = cur.fetchone()
                db_password = result[0] if result else None
            else:
                cur.execute("""
                    SELECT password FROM students WHERE id = ?
                """, (user['id'],))
                result = cur.fetchone()
                db_password = result['password'] if result else None
            
            if db_password and db_password.startswith('$2'):
                print(f"  ✓ Verified: {user['username']} now has bcrypt hash")
            else:
                print(f"  ✗ Still unhashed: {user['username']}")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_csv_logins():
    """Verify CSV users can now login"""
    print("\n[4] Verifying CSV logins now work...")
    
    try:
        import subprocess
        result = subprocess.run(['python', 'DEBUG_CSV_LOGIN.py'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✓ Verification script completed")
            # Check output for success
            if "ALL CSV users can login" in result.stdout:
                print("  ✓ All CSV users can now login!")
                return True
        
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║           CSV USER PASSWORD FIXER                              ║
    ║      Fixes unhashed passwords from CSV import                  ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    if fix_csv_passwords():
        print("\n✓ Passwords fixed successfully!")
        print("\nYou can now test logins with:")
        print("  python DEBUG_CSV_LOGIN.py")
        print("\nOr test in browser:")
        print("  Username: jdoe")
        print("  Password: password123")
    else:
        print("\n✗ Failed to fix passwords")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
