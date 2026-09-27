#!/usr/bin/env python3
"""
Mengo-Hub System Setup and Fix Script
Initializes system, fixes issues, and creates permanent admin certificate for A000
"""

import os
import sys
import sqlite3
import psycopg2
import psycopg2.extras
import bcrypt
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
ADMIN_ID = os.getenv('ADMIN_ID', 'A000')
ADMIN_USERNAME = os.getenv('ADMIN_SECRET_KEY', 'Newton')
ADMIN_PASSWORD = os.getenv('ADMIN_SECRET_PASSWORD', '##0000')
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'postgresql').lower()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:##0000@localhost:5432/mengo_hub')

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_db_connection():
    """Get database connection based on type"""
    try:
        if DATABASE_TYPE == 'postgresql':
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        else:
            sqlite_path = DATABASE_URL if DATABASE_URL else 'data/mengo.db'
            conn = sqlite3.connect(sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        sys.exit(1)

def generate_admin_certificate(admin_id):
    """Generate a permanent admin certificate for A000"""
    cert_data = f"{admin_id}:{datetime.utcnow().isoformat()}:{os.urandom(32).hex()}"
    certificate = hashlib.sha256(cert_data.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(days=3650)  # 10 years
    return certificate, expires_at

def create_admin_certificate_in_db(conn, admin_id):
    """Create permanent admin certificate in database"""
    try:
        certificate, expires_at = generate_admin_certificate(admin_id)
        
        if DATABASE_TYPE == 'postgresql':
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO super_admin_certificates 
                (certificate_id, admin_id, certificate_code, issued_at, expires_at, is_active, issued_by)
                VALUES (%s, %s, %s, %s, %s, 1, %s)
                ON CONFLICT (admin_id) DO UPDATE SET
                    certificate_code = EXCLUDED.certificate_code,
                    issued_at = EXCLUDED.issued_at,
                    expires_at = EXCLUDED.expires_at,
                    is_active = 1
            """, (
                f"CERT_{admin_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                admin_id,
                certificate,
                datetime.utcnow(),
                expires_at,
                admin_id
            ))
        else:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO super_admin_certificates 
                (admin_id, certificate_code, issued_at, expires_at, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (
                admin_id,
                certificate,
                datetime.utcnow().isoformat(),
                expires_at.isoformat()
            ))
        
        conn.commit()
        print(f"✓ Created permanent admin certificate for {admin_id}")
        print(f"  Certificate expires: {expires_at}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create admin certificate: {e}")
        return False

def verify_admin_user_exists(conn):
    """Verify A000 admin user exists and has correct credentials"""
    try:
        if DATABASE_TYPE == 'postgresql':
            # Import RealDictCursor safely
            try:
                from psycopg2.extras import RealDictCursor
                cur = conn.cursor(cursor_factory=RealDictCursor)
            except ImportError:
                # Fallback if extras not available
                cur = conn.cursor()
        else:
            cur = conn.cursor()
        
        cur.execute('SELECT * FROM students WHERE id = ?', (ADMIN_ID,))
        user = cur.fetchone()
        
        if not user:
            print(f"Creating admin user {ADMIN_ID}...")
            hashed_pwd = hash_password(ADMIN_PASSWORD)
            if DATABASE_TYPE == 'postgresql':
                cur.execute("""
                    INSERT INTO students 
                    (id, username, password, fullName, email, stream, class, role, is_admin, payment_status, createdAt)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, 'paid', CURRENT_TIMESTAMP)
                    ON CONFLICT DO NOTHING
                """, (ADMIN_ID, ADMIN_USERNAME, hashed_pwd, 'System Administrator', 'admin@mengo.com', 'All', 'All', 'System Administrator'))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO students 
                    (id, username, password, fullName, email, stream, class, role, is_admin, payment_status, createdAt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'paid', CURRENT_TIMESTAMP)
                """, (ADMIN_ID, ADMIN_USERNAME, hashed_pwd, 'System Administrator', 'admin@mengo.com', 'All', 'All', 'System Administrator'))
            conn.commit()
            print(f"✓ Admin user {ADMIN_ID} created successfully")
        else:
            print(f"✓ Admin user {ADMIN_ID} already exists")
        return True
    except Exception as e:
        print(f"ERROR: Failed to verify/create admin user: {e}")
        return False

def test_login_functionality():
    """Test that login works for different user types"""
    print("\n--- Testing Login Functionality ---")
    try:
        from flask_app import app, get_db
        
        with app.test_client() as client:
            # Test admin login
            print("Testing admin login...")
            response = client.post('/api/login', json={
                'username': ADMIN_USERNAME,
                'password': ADMIN_PASSWORD
            })
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"✓ Admin login works: {data.get('message')}")
                else:
                    print(f"✗ Admin login failed: {data.get('message')}")
            else:
                print(f"✗ Admin login error: HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠ Skipping login test: {e}")

def organize_project_structure():
    """Organize project files into logical folders"""
    print("\n--- Organizing Project Structure ---")
    
    folders = [
        'src/services',
        'src/routes',
        'src/utils',
        'src/middleware',
        'config',
        'templates',
        'public/css',
        'public/js',
        'public/images',
        'data/imports',
        'logs',
        'uploads/documents',
        'uploads/audio',
        'uploads/videos',
        'uploads/images',
        'tests',
        'docs'
    ]
    
    for folder in folders:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {folder}/")
    
    # Create README for structure
    readme_content = """# Mengo-Hub System Structure

## Folders

- **src/services** - Core business logic services (admin, auth, email, etc.)
- **src/routes** - API route handlers
- **src/utils** - Utility functions
- **src/middleware** - Flask middleware
- **config** - Configuration files
- **templates** - HTML templates
- **public** - Static files (CSS, JS, images)
- **data** - Data files and imports
- **logs** - Application logs
- **uploads** - User uploads
- **tests** - Test files
- **docs** - Documentation

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Run setup: `python SETUP_AND_FIX.py`
3. Start app: `python run.py`
"""
    
    with open('STRUCTURE.md', 'w') as f:
        f.write(readme_content)
    print("✓ Created STRUCTURE.md")

def main():
    print("=" * 60)
    print("Mengo-Hub System Setup and Fix")
    print("=" * 60)
    
    # Step 1: Connect to database
    print("\n--- Connecting to Database ---")
    conn = get_db_connection()
    print(f"✓ Connected to {DATABASE_TYPE} database")
    
    # Step 2: Verify admin user
    print("\n--- Verifying Admin User ---")
    if not verify_admin_user_exists(conn):
        conn.close()
        sys.exit(1)
    
    # Step 3: Create permanent admin certificate
    print("\n--- Creating Admin Certificate ---")
    if not create_admin_certificate_in_db(conn, ADMIN_ID):
        conn.close()
        sys.exit(1)
    
    # Step 4: Organize project
    organize_project_structure()
    
    # Step 5: Close connection
    conn.close()
    
    # Step 6: Test login
    test_login_functionality()
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review STRUCTURE.md for project organization")
    print("2. Set environment variables in .env file")
    print("3. Run: python run.py")
    print("=" * 60)

if __name__ == '__main__':
    main()
