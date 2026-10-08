"""
Quick Database Initialization Script
Creates a default admin user for testing
"""

import sqlite3
import bcrypt
from datetime import datetime

def init_database():
    # Connect to SQLite database
    conn = sqlite3.connect('mengo_hub.db')
    cursor = conn.cursor()
    
    # Create basic tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullName TEXT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            stream TEXT,
            class TEXT,
            role TEXT DEFAULT 'student',
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullName TEXT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            subjects TEXT,
            role TEXT DEFAULT 'teacher',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user
    admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute('''
            INSERT INTO students (fullName, username, password, email, stream, class, role, is_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Admin User', 'admin', admin_password.decode('utf-8'), 'admin@mengohub.ug', 'S6', 'S6', 'admin', 1))
        
        conn.commit()
        print("✅ Default admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Please change this password after first login!")
        
    except sqlite3.IntegrityError:
        print("⚠️ Admin user already exists")
    
    # Create a test student user
    student_password = bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute('''
            INSERT INTO students (fullName, username, password, email, stream, class, role, is_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Test Student', 'student', student_password.decode('utf-8'), 'student@mengohub.ug', 'S4', 'S4', 'student', 0))
        
        conn.commit()
        print("✅ Test student user created successfully!")
        print("Username: student")
        print("Password: student123")
        
    except sqlite3.IntegrityError:
        print("⚠️ Student user already exists")
    
    conn.close()
    print("\n🎉 Database initialization complete!")
    print("You can now login at http://localhost:5000/login.html")

if __name__ == '__main__':
    init_database()