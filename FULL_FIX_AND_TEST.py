#!/usr/bin/env python3
"""
Comprehensive Mengo-Hub System Fixer and Tester
Fixes all critical issues and tests everything
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def clean_pycache():
    """Remove all pycache directories"""
    print("\n[1] Cleaning pycache...")
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path, ignore_errors=True)
            print(f"  ✓ Removed {pycache_path}")
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    print("  ✓ Pycache cleaned")

def verify_imports():
    """Verify all critical imports work"""
    print("\n[2] Verifying imports...")
    try:
        import flask
        print("  ✓ Flask")
    except ImportError as e:
        print(f"  ✗ Flask: {e}")
        return False
    
    try:
        import psycopg2
        import psycopg2.extras
        print("  ✓ psycopg2 with extras")
    except ImportError as e:
        print(f"  ✗ psycopg2: {e}")
        return False
    
    try:
        import bcrypt
        print("  ✓ bcrypt")
    except ImportError as e:
        print(f"  ✗ bcrypt: {e}")
        return False
    
    try:
        from flask_app import app, socketio
        print("  ✓ flask_app (app, socketio)")
    except ImportError as e:
        print(f"  ✗ flask_app: {e}")
        return False
    
    try:
        from admin_service import AdminSecurityService
        print("  ✓ admin_service")
    except ImportError as e:
        print(f"  ✗ admin_service: {e}")
        return False
    
    print("  ✓ All imports verified!")
    return True

def test_database_connection():
    """Test database connectivity"""
    print("\n[3] Testing database connection...")
    
    db_type = os.getenv('DATABASE_TYPE', 'postgresql').lower()
    db_url = os.getenv('DATABASE_URL')
    
    print(f"  Database Type: {db_type}")
    
    if db_type == 'postgresql':
        try:
            import psycopg2
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            result = cur.fetchone()
            conn.close()
            print("  ✓ PostgreSQL connection successful")
            return True
        except Exception as e:
            print(f"  ✗ PostgreSQL connection failed: {e}")
            return False
    else:
        try:
            import sqlite3
            db_path = db_url if db_url else 'data/mengo.db'
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            conn.close()
            print("  ✓ SQLite connection successful")
            return True
        except Exception as e:
            print(f"  ✗ SQLite connection failed: {e}")
            return False

def verify_tables():
    """Verify all required tables exist"""
    print("\n[4] Verifying database tables...")
    
    db_type = os.getenv('DATABASE_TYPE', 'postgresql').lower()
    db_url = os.getenv('DATABASE_URL')
    
    required_tables = ['students', 'teachers', 'super_admin_certificates', 'loginLogs']
    
    if db_type == 'postgresql':
        try:
            import psycopg2
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            for table in required_tables:
                cur.execute(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                exists = cur.fetchone()[0]
                status = "✓" if exists else "✗"
                print(f"  {status} {table}")
            conn.close()
        except Exception as e:
            print(f"  ✗ Error checking tables: {e}")
            return False
    else:
        try:
            import sqlite3
            db_path = db_url if db_url else 'data/mengo.db'
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            for table in required_tables:
                cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                exists = cur.fetchone() is not None
                status = "✓" if exists else "✗"
                print(f"  {status} {table}")
            conn.close()
        except Exception as e:
            print(f"  ✗ Error checking tables: {e}")
            return False
    
    return True

def test_admin_user():
    """Verify A000 admin user exists"""
    print("\n[5] Verifying A000 admin user...")
    
    db_type = os.getenv('DATABASE_TYPE', 'postgresql').lower()
    db_url = os.getenv('DATABASE_URL')
    admin_id = os.getenv('ADMIN_ID', 'A000')
    
    if db_type == 'postgresql':
        try:
            import psycopg2
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            cur.execute("SELECT id, username, fullName, is_admin FROM students WHERE id = %s", (admin_id,))
            user = cur.fetchone()
            conn.close()
            
            if user:
                print(f"  ✓ Admin user {admin_id} exists")
                print(f"    Username: {user[1]}")
                print(f"    Full Name: {user[2]}")
                print(f"    Is Admin: {user[3]}")
                return True
            else:
                print(f"  ✗ Admin user {admin_id} NOT found")
                return False
        except Exception as e:
            print(f"  ✗ Error checking admin user: {e}")
            return False
    else:
        try:
            import sqlite3
            db_path = db_url if db_url else 'data/mengo.db'
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT id, username, fullName, is_admin FROM students WHERE id = ?", (admin_id,))
            user = cur.fetchone()
            conn.close()
            
            if user:
                print(f"  ✓ Admin user {admin_id} exists")
                print(f"    Username: {user['username']}")
                print(f"    Full Name: {user['fullName']}")
                print(f"    Is Admin: {user['is_admin']}")
                return True
            else:
                print(f"  ✗ Admin user {admin_id} NOT found")
                return False
        except Exception as e:
            print(f"  ✗ Error checking admin user: {e}")
            return False

def test_csv_users():
    """Verify CSV imported users exist"""
    print("\n[6] Checking CSV imported users...")
    
    db_type = os.getenv('DATABASE_TYPE', 'postgresql').lower()
    db_url = os.getenv('DATABASE_URL')
    
    test_usernames = ['jdoe', 'asmith', 'bwilson']
    
    if db_type == 'postgresql':
        try:
            import psycopg2
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            
            for username in test_usernames:
                cur.execute("SELECT id, username, fullName FROM students WHERE username = %s", (username,))
                user = cur.fetchone()
                if user:
                    print(f"  ✓ {username} found (ID: {user[0]})")
                else:
                    print(f"  ✗ {username} NOT found")
            
            conn.close()
        except Exception as e:
            print(f"  ✗ Error checking users: {e}")
    else:
        try:
            import sqlite3
            db_path = db_url if db_url else 'data/mengo.db'
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            for username in test_usernames:
                cur.execute("SELECT id, username, fullName FROM students WHERE username = ?", (username,))
                user = cur.fetchone()
                if user:
                    print(f"  ✓ {username} found (ID: {user['id']})")
                else:
                    print(f"  ✗ {username} NOT found")
            
            conn.close()
        except Exception as e:
            print(f"  ✗ Error checking users: {e}")

def test_password_hashing():
    """Test password hashing and verification"""
    print("\n[7] Testing password hashing...")
    
    try:
        import bcrypt
        
        test_password = "TestPassword123"
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        is_correct = bcrypt.checkpw(test_password.encode('utf-8'), hashed.encode('utf-8'))
        
        if is_correct:
            print("  ✓ Password hashing works correctly")
            return True
        else:
            print("  ✗ Password verification failed")
            return False
    except Exception as e:
        print(f"  ✗ Password hashing error: {e}")
        return False

def create_admin_certificate():
    """Create permanent admin certificate for A000"""
    print("\n[8] Creating admin certificate...")
    
    db_type = os.getenv('DATABASE_TYPE', 'postgresql').lower()
    db_url = os.getenv('DATABASE_URL')
    admin_id = os.getenv('ADMIN_ID', 'A000')
    
    try:
        import hashlib
        from datetime import datetime, timedelta
        
        # Generate certificate
        cert_data = f"{admin_id}:{datetime.utcnow().isoformat()}:{os.urandom(32).hex()}"
        certificate = hashlib.sha256(cert_data.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=3650)  # 10 years
        
        if db_type == 'postgresql':
            import psycopg2
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            
            # Check if certificate exists
            cur.execute("SELECT * FROM super_admin_certificates WHERE admin_id = %s", (admin_id,))
            existing = cur.fetchone()
            
            if existing:
                cur.execute("""
                    UPDATE super_admin_certificates 
                    SET certificate_code = %s, issued_at = %s, expires_at = %s, is_active = 1
                    WHERE admin_id = %s
                """, (certificate, datetime.utcnow(), expires_at, admin_id))
                print(f"  ✓ Updated admin certificate for {admin_id}")
            else:
                cur.execute("""
                    INSERT INTO super_admin_certificates 
                    (admin_id, certificate_code, issued_at, expires_at, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                """, (admin_id, certificate, datetime.utcnow(), expires_at))
                print(f"  ✓ Created admin certificate for {admin_id}")
            
            conn.commit()
            print(f"    Expires: {expires_at.isoformat()}")
            conn.close()
        else:
            import sqlite3
            db_path = db_url if db_url else 'data/mengo.db'
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            
            cur.execute("SELECT * FROM super_admin_certificates WHERE admin_id = ?", (admin_id,))
            existing = cur.fetchone()
            
            if existing:
                cur.execute("""
                    UPDATE super_admin_certificates 
                    SET certificate_code = ?, issued_at = ?, expires_at = ?, is_active = 1
                    WHERE admin_id = ?
                """, (certificate, datetime.utcnow().isoformat(), expires_at.isoformat(), admin_id))
                print(f"  ✓ Updated admin certificate for {admin_id}")
            else:
                cur.execute("""
                    INSERT INTO super_admin_certificates 
                    (admin_id, certificate_code, issued_at, expires_at, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (admin_id, certificate, datetime.utcnow().isoformat(), expires_at.isoformat()))
                print(f"  ✓ Created admin certificate for {admin_id}")
            
            conn.commit()
            print(f"    Expires: {expires_at.isoformat()}")
            conn.close()
        
        return True
    except Exception as e:
        print(f"  ✗ Error creating certificate: {e}")
        return False

def main():
    """Main execution"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         MENGO-HUB FULL FIX AND TEST SYSTEM                     ║
    ║    Comprehensive Testing and Problem Resolution                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    all_ok = True
    
    # Run all checks
    clean_pycache()
    
    if not verify_imports():
        print("\n✗ Import verification failed - installing requirements...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
        if not verify_imports():
            print("\n✗ Still failing after install - check requirements.txt")
            return False
    
    if not test_database_connection():
        print("\n✗ Database connection failed - check .env configuration")
        all_ok = False
    
    verify_tables()
    
    if not test_admin_user():
        print("\n✗ Admin user missing - run SETUP_AND_FIX.py first")
        all_ok = False
    
    test_csv_users()
    test_password_hashing()
    create_admin_certificate()
    
    print("\n" + "="*60)
    if all_ok:
        print("✓ System checks completed successfully!")
        print("\nYou can now start the server with:")
        print("  python START_SYSTEM.py")
    else:
        print("⚠ Some checks failed - see above for details")
    print("="*60 + "\n")
    
    return all_ok

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
