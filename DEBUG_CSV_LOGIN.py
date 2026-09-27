#!/usr/bin/env python3
"""
CSV Login Debugging Script
Identifies why CSV imported users can't login
"""

import bcrypt
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'postgresql').lower()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:##000000@localhost:5432/mengo_hub')

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

def test_user_login(username, password):
    """Test a specific user login"""
    print(f"\n{'='*60}")
    print(f"Testing: {username} / {password}")
    print('='*60)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Search in students table
        if DATABASE_TYPE == 'postgresql':
            cur.execute("SELECT id, username, password, is_admin, payment_status FROM students WHERE username = %s", (username,))
            user = cur.fetchone()
            user_table = 'students'
        else:
            cur.execute("SELECT id, username, password, is_admin, payment_status FROM students WHERE username = ?", (username,))
            user = cur.fetchone()
            user_table = 'students'
        
        if not user:
            # Search in teachers table
            if DATABASE_TYPE == 'postgresql':
                cur.execute("SELECT id, username, password, is_admin, payment_status FROM teachers WHERE username = %s", (username,))
                user = cur.fetchone()
                user_table = 'teachers'
            else:
                cur.execute("SELECT id, username, password, is_admin, payment_status FROM teachers WHERE username = ?", (username,))
                user = cur.fetchone()
                user_table = 'teachers'
        
        if not user:
            print(f"✗ User '{username}' NOT FOUND in database!")
            conn.close()
            return False
        
        # Extract user data
        if DATABASE_TYPE == 'postgresql':
            user_id, db_username, db_password, is_admin, payment_status = user
        else:
            user_id = user['id']
            db_username = user['username']
            db_password = user['password']
            is_admin = user['is_admin']
            payment_status = user['payment_status']
        
        print(f"✓ User found in '{user_table}' table")
        print(f"  ID: {user_id}")
        print(f"  Username: {db_username}")
        print(f"  Is Admin: {is_admin}")
        print(f"  Payment Status: {payment_status}")
        print(f"  Password Hash Exists: {bool(db_password)}")
        
        if not db_password:
            print(f"✗ PROBLEM: No password hash stored in database!")
            conn.close()
            return False
        
        # Try to verify password
        try:
            password_bytes = password.encode('utf-8')
            db_password_bytes = db_password.encode('utf-8') if isinstance(db_password, str) else db_password
            
            # Check if it's a valid bcrypt hash
            if not db_password_bytes.startswith(b'$2'):
                print(f"✗ PROBLEM: Password is not bcrypt hash! (starts with: {db_password_bytes[:10]})")
                conn.close()
                return False
            
            # Verify password
            is_correct = bcrypt.checkpw(password_bytes, db_password_bytes)
            
            if is_correct:
                print(f"✓ Password matches!")
                print(f"✓ LOGIN WOULD SUCCEED")
            else:
                print(f"✗ PROBLEM: Password does NOT match!")
                print(f"  Expected: Bcrypt hash of '{password}'")
                print(f"  Got: {db_password[:50]}...")
            
            print(f"\nPayment Status Check: {payment_status}")
            if payment_status and payment_status != 'paid':
                print(f"⚠ WARNING: Payment status is '{payment_status}', not 'paid'")
                print(f"  This will block login with 402 Payment Required")
            elif payment_status == 'paid':
                print(f"✓ Payment status is 'paid' - OK")
            else:
                print(f"⚠ WARNING: Payment status is empty or NULL")
            
            conn.close()
            return is_correct
        
        except ValueError as e:
            print(f"✗ PROBLEM: Bcrypt error - {e}")
            print(f"  The password hash might be corrupted")
            conn.close()
            return False
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_password_hashing():
    """Test password hashing system"""
    print(f"\n{'='*60}")
    print("Testing Password Hashing System")
    print('='*60)
    
    try:
        # Test 1: Hash a new password
        test_password = "password123"
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"\n1. Generated hash for '{test_password}':")
        print(f"   {hashed}")
        
        # Test 2: Verify it
        is_correct = bcrypt.checkpw(test_password.encode('utf-8'), hashed.encode('utf-8'))
        print(f"2. Verification: {is_correct}")
        
        if is_correct:
            print("✓ Password hashing system working correctly")
            return True
        else:
            print("✗ Password hashing verification failed!")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║           CSV LOGIN DEBUGGING SCRIPT                           ║
    ║      Identifies why CSV users can't login                      ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Test password hashing system
    test_password_hashing()
    
    # Test admin login (should work)
    print("\n\n" + "="*60)
    print("TESTING WORKING ACCOUNT (Admin)")
    print("="*60)
    test_user_login("Newton", "##0000")
    
    # Test CSV users
    print("\n\n" + "="*60)
    print("TESTING CSV IMPORTED ACCOUNTS")
    print("="*60)
    
    csv_users = [
        ("jdoe", "password123"),
        ("asmith", "password123"),
        ("bwilson", "password123"),
        ("jane_smith", "password123"),
        ("mike_jones", "password123"),
    ]
    
    results = {}
    for username, password in csv_users:
        success = test_user_login(username, password)
        results[username] = success
    
    # Summary
    print("\n\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for username, success in results.items():
        status = "✓ CAN LOGIN" if success else "✗ CANNOT LOGIN"
        print(f"{status}: {username}")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    failed_count = sum(1 for v in results.values() if not v)
    if failed_count == 0:
        print("✓ All CSV users can login!")
        print("  Problem may be on client side or in request handling")
    elif failed_count == len(results):
        print("✗ NO CSV users can login!")
        print("  Possible causes:")
        print("    1. CSV import didn't save password hashes")
        print("    2. Password hashing function not working")
        print("    3. Need to re-import users from CSV")
    else:
        print("⚠ Some users can login, some can't")
        print("  This suggests inconsistent data in database")
    
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
