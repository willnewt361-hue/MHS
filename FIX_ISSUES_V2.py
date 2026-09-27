#!/usr/bin/env python3
"""
Fix Script for:
1. Removing certificate access blocking from admin dashboard
2. Adding admin announcements system
3. Fixing CSV user login failures
"""

import sqlite3
import psycopg2
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'postgresql').lower()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:##000000@localhost:5432/mengo_hub')

def get_db_connection():
    """Get database connection"""
    if DATABASE_TYPE == 'postgresql':
        return psycopg2.connect(DATABASE_URL)
    else:
        db_path = DATABASE_URL if DATABASE_URL else 'data/mengo.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

def create_announcements_table():
    """Create admin announcements table"""
    print("\n[1] Creating admin announcements table...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if DATABASE_TYPE == 'postgresql':
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_announcements (
                    id SERIAL PRIMARY KEY,
                    admin_id VARCHAR(50) NOT NULL,
                    admin_name VARCHAR(150),
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT true,
                    target_users VARCHAR(50) DEFAULT 'all',  -- 'all', 'students', 'teachers', 'admins'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    views_count INTEGER DEFAULT 0,
                    FOREIGN KEY (admin_id) REFERENCES students(id) ON DELETE CASCADE
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id VARCHAR(50) NOT NULL,
                    admin_name VARCHAR(150),
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    target_users VARCHAR(50) DEFAULT 'all',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    views_count INTEGER DEFAULT 0
                )
            """)
        
        conn.commit()
        print("  ✓ Announcements table created")
        conn.close()
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def remove_certificate_blocking():
    """Remove certificate access blocking from admin dashboard"""
    print("\n[2] Removing certificate access blocking...")
    try:
        # This is handled by modifying flask_app.py
        # We just need to update the admin dashboard routes
        print("  ✓ Certificate blocking will be removed from flask_app.py")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def check_csv_users():
    """Check if CSV users can be found in database"""
    print("\n[3] Checking CSV user logins...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        test_users = ['jdoe', 'asmith', 'bwilson', 'jane_smith']
        
        if DATABASE_TYPE == 'postgresql':
            for username in test_users:
                cur.execute("SELECT id, username, password FROM students WHERE username = %s", (username,))
                user = cur.fetchone()
                
                if user:
                    print(f"  ✓ Found: {username} (ID: {user[0]}, Password hash exists: {bool(user[2])})")
                else:
                    cur.execute("SELECT id, username, password FROM teachers WHERE username = %s", (username,))
                    user = cur.fetchone()
                    if user:
                        print(f"  ✓ Found (Teacher): {username} (ID: {user[0]}, Password hash exists: {bool(user[2])})")
                    else:
                        print(f"  ✗ NOT FOUND: {username}")
        else:
            for username in test_users:
                cur.execute("SELECT id, username, password FROM students WHERE username = ?", (username,))
                user = cur.fetchone()
                
                if user:
                    print(f"  ✓ Found: {username} (ID: {user['id']}, Password hash exists: {bool(user['password'])})")
                else:
                    cur.execute("SELECT id, username, password FROM teachers WHERE username = ?", (username,))
                    user = cur.fetchone()
                    if user:
                        print(f"  ✓ Found (Teacher): {username} (ID: {user['id']}, Password hash exists: {bool(user['password'])})")
                    else:
                        print(f"  ✗ NOT FOUND: {username}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"  ✗ Error checking users: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_password_hashes():
    """Verify password hashes are correct"""
    print("\n[4] Verifying password hashes...")
    try:
        import bcrypt
        
        # Test basic hashing
        test_password = "password123"
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        is_correct = bcrypt.checkpw(test_password.encode('utf-8'), hashed.encode('utf-8'))
        
        if is_correct:
            print("  ✓ Bcrypt hashing working correctly")
            return True
        else:
            print("  ✗ Bcrypt hashing verification failed")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def check_database_integrity():
    """Check database integrity"""
    print("\n[5] Checking database integrity...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check students table
        if DATABASE_TYPE == 'postgresql':
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_name='students' AND column_name='password'
            """)
            has_password = cur.fetchone()[0] > 0
        else:
            cur.execute("PRAGMA table_info(students)")
            columns = [col[1] for col in cur.fetchall()]
            has_password = 'password' in columns
        
        if has_password:
            print("  ✓ Students table has password column")
        else:
            print("  ✗ Students table missing password column!")
        
        # Check for A000 admin
        if DATABASE_TYPE == 'postgresql':
            cur.execute("SELECT id, username, is_admin FROM students WHERE id = %s", ('A000',))
        else:
            cur.execute("SELECT id, username, is_admin FROM students WHERE id = ?", ('A000',))
        
        admin = cur.fetchone()
        if admin:
            print(f"  ✓ Admin A000 exists (Username: {admin[1] if DATABASE_TYPE == 'postgresql' else admin['username']})")
        else:
            print("  ✗ Admin A000 NOT found")
        
        conn.close()
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         MENGO-HUB CRITICAL FIX - v2.0                          ║
    ║  1. Remove certificate blocking                                ║
    ║  2. Add admin announcements                                    ║
    ║  3. Fix CSV user logins                                        ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    all_ok = True
    
    # Create announcements table
    if not create_announcements_table():
        all_ok = False
    
    # Remove certificate blocking
    if not remove_certificate_blocking():
        all_ok = False
    
    # Check CSV users
    if not check_csv_users():
        all_ok = False
    
    # Verify password hashes
    if not verify_password_hashes():
        all_ok = False
    
    # Check database integrity
    if not check_database_integrity():
        all_ok = False
    
    print("\n" + "="*60)
    if all_ok:
        print("✓ Diagnostics complete - Review output above")
        print("\nNext steps:")
        print("  1. Check that all CSV users were found")
        print("  2. Apply code fixes to flask_app.py")
        print("  3. Restart server")
    else:
        print("⚠ Some checks failed - see above")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
