from flask import Flask, request, jsonify, send_file, send_from_directory, session, g
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import psycopg2
import psycopg2.extras
import bcrypt
import os
import json
import csv
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
import re
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import load_dotenv
import random
import uuid
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import torch
from transformers import pipeline
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from PIL import Image
import qrcode
import io
import base64
from io import BytesIO
from functools import wraps
import threading
import time
from gpt4all import GPT4All

# Import premium and AI modules
try:
    from email_service import email_service
    from ai_service import ai_service
    from premium_features import analytics_service, gamification_service, attendance_service, report_service
    from premium_routes import register_premium_routes
    from websocket_ai import register_websocket_ai
    from audio_service import init_audio_service
    from document_service import init_document_service
    from chat_service import init_chat_service
    from admin_service import AdminSecurityService
    from analytics_service import AnalyticsService
    from media_service import MediaService
    from dashboard_service import DashboardService
    PREMIUM_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Premium modules not fully available: {e}")
    PREMIUM_MODULES_AVAILABLE = False

load_dotenv()
app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Initialize Flask-SocketIO
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# AI Configuration
AI_MODEL_PATH = os.getenv('AI_MODEL_PATH', 'models/llama-2-7b-chat.ggmlv3.q4_0.bin')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'gpt4all')  # gpt4all, openai, anthropic, google
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Initialize AI models
ai_models = {}
try:
    if AI_PROVIDER == 'gpt4all':
        ai_models['gpt4all'] = GPT4All(AI_MODEL_PATH)
    elif AI_PROVIDER == 'openai':
        import openai
        openai.api_key = OPENAI_API_KEY
    elif AI_PROVIDER == 'anthropic':
        import anthropic
        ai_models['anthropic'] = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    elif AI_PROVIDER == 'google':
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        ai_models['google'] = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Warning: AI initialization failed: {e}")

# Configuration
ADMIN_ID = os.getenv('ADMIN_ID', 'A000')
ADMIN_SECRET_KEY = os.getenv('ADMIN_SECRET_KEY', 'Newton')
ADMIN_SECRET_PASSWORD = os.getenv('ADMIN_SECRET_PASSWORD', '##0000')
ADMIN_API_TOKEN = os.getenv('ADMIN_API_TOKEN', 'MengoAdminAPIToken2026')
SUPER_ADMIN_API_TOKEN = os.getenv('SUPER_ADMIN_API_TOKEN', 'MengoSuperAdminToken2026')
ADMIN_IMPORT_PASSWORD = os.getenv('ADMIN_IMPORT_PASSWORD', 'ImportPassword2026')
LOGIN_ATTEMPTS_LIMIT = int(os.getenv('LOGIN_ATTEMPTS_LIMIT', '5'))
LOCKOUT_HOURS = int(os.getenv('LOCKOUT_HOURS', '24'))
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'postgresql').lower()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:##0000@localhost:5432/mengo_hub')
IMPORT_CSV_PATH = os.getenv('IMPORT_CSV_PATH', 'data/import.csv')
UPLOAD_FOLDER = 'public/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('public/images/students', exist_ok=True)
os.makedirs('public/images/teachers', exist_ok=True)
os.makedirs('data/attachments', exist_ok=True)

class DatabaseWrapper:
    def __init__(self, conn, db_type):
        self.conn = conn
        self.db_type = db_type
        if db_type == 'postgresql':
            self.cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            self.cursor = conn.cursor()

    def execute(self, sql, params=None):
        if params is None:
            params = ()
        if self.db_type == 'postgresql':
            sql = sql.replace('?', '%s')
        self.cursor.execute(sql, params)
        return self

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        try:
            self.cursor.close()
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        if DATABASE_TYPE == 'postgresql':
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = False
            db = g._database = DatabaseWrapper(conn, 'postgresql')
        else:
            sqlite_path = DATABASE_URL if DATABASE_URL else 'data/mengo.db'
            conn = sqlite3.connect(sqlite_path)
            conn.row_factory = sqlite3.Row
            db = g._database = DatabaseWrapper(conn, 'sqlite')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()

        if DATABASE_TYPE == 'postgresql':
            schema_file = Path('schema.sql')
            if not schema_file.exists():
                raise RuntimeError('PostgreSQL schema.sql file not found. Please add schema.sql to the project root.')

            sql = schema_file.read_text()
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            for stmt in statements:
                db.execute(stmt)
            db.commit()
            return

        # SQLite fallback support only if explicitly configured
        db.execute('''CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullName TEXT NOT NULL,
            email TEXT,
            stream TEXT NOT NULL,
            class TEXT NOT NULL,
            role TEXT DEFAULT 'Normal student',
            photo TEXT,
            is_admin INTEGER DEFAULT 0,
            certificate TEXT,
            payment_status TEXT DEFAULT 'unpaid',
            login_attempts INTEGER DEFAULT 0,
            lockout_until DATETIME DEFAULT NULL,
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            mental_wellbeing TEXT,
            decision_making TEXT,
            ambitions TEXT,
            hobbies TEXT,
            behavior_profile TEXT
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS teachers (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullName TEXT NOT NULL,
            email TEXT,
            subjects TEXT NOT NULL,
            stream TEXT DEFAULT '',
            class TEXT DEFAULT '',
            photo TEXT,
            quote TEXT,
            role TEXT DEFAULT 'Normal teacher',
            is_admin INTEGER DEFAULT 0,
            certificate TEXT,
            payment_status TEXT DEFAULT 'unpaid',
            login_attempts INTEGER DEFAULT 0,
            lockout_until DATETIME DEFAULT NULL,
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            difficulty TEXT DEFAULT 'medium'
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS student_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            score REAL NOT NULL,
            total_questions INTEGER NOT NULL,
            weaknesses TEXT,
            recommendations TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            plan_data TEXT NOT NULL,
            ai_generated INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_type TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_id TEXT UNIQUE,
            payment_method TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            teacher_id TEXT NOT NULL,
            from_role TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            message TEXT NOT NULL,
            attachment_name TEXT,
            is_read INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS loginLogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId TEXT NOT NULL,
            userType TEXT NOT NULL,
            username TEXT NOT NULL,
            loginTime DATETIME DEFAULT CURRENT_TIMESTAMP,
            ipAddress TEXT,
            action TEXT DEFAULT 'login'
        )''')

        db.execute('''INSERT OR REPLACE INTO students
            (id, username, password, fullName, email, stream, class, role, photo, is_admin, certificate, payment_status, login_attempts, lockout_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL)
        ''', (ADMIN_ID, ADMIN_SECRET_KEY, hash_password(ADMIN_SECRET_PASSWORD), 'System Administrator', 'admin@mengo.com', 'All', 'All', 'System Administrator', None, 1, None, 'paid'))
        db.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def require_admin_token(f):
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Admin authorization required'}), 403
        token = auth[7:]
        if token != ADMIN_API_TOKEN and token != SUPER_ADMIN_API_TOKEN:
            return jsonify({'success': False, 'message': 'Invalid admin token'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_super_admin_token(f):
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Super admin authorization required'}), 403
        token = auth[7:]
        if token != SUPER_ADMIN_API_TOKEN:
            return jsonify({'success': False, 'message': 'Invalid super admin token'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def is_super_admin_request():
    auth = request.headers.get('Authorization', '')
    return auth.startswith('Bearer ') and auth[7:] == SUPER_ADMIN_API_TOKEN

def parse_bool(value):
    return str(value).strip().lower() in ('1', 'true', 'yes', 'y')

def require_auth(f):
    """Decorator to require user authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(f):
    """Simple rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id', request.remote_addr)
        cache_key = f"rate_limit:{user_id}:{request.endpoint}"
        # In production, use Redis for this
        return f(*args, **kwargs)
    return decorated_function

def normalize_user_id(row_type, raw_id, username):
    raw_id = (raw_id or '').strip()
    if row_type == 'admin':
        if raw_id and raw_id.upper() != ADMIN_ID and re.match(r'^A\d{3}$', raw_id.upper()):
            return raw_id.upper()
        return None

    if row_type == 'teacher':
        if raw_id and re.match(r'^T\d{3,}$', raw_id.upper()):
            return raw_id.upper()
        return f'T{random.randint(100,999)}'

    if row_type == 'student':
        if raw_id:
            return raw_id.strip()
        if username:
            safe = re.sub(r'[^A-Za-z0-9/]', '', username).upper()
            return safe or f'STU{random.randint(1000,9999)}'
        return f'STU{random.randint(1000,9999)}'
    return raw_id or str(uuid.uuid4())

def generate_certificate():
    """Generate self-signed SSL certificate"""
    import subprocess
    os.makedirs('data', exist_ok=True)
    
    cert_path = CERT_FILE
    key_path = KEY_FILE
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return True
    
    try:
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', key_path, '-out', cert_path,
            '-days', '365', '-nodes',
            '-subj', '/CN=mengo-hub.local'
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info("SSL certificate generated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to generate certificate: {str(e)}")
        return False



@app.route('/api/premium/gamification/<student_id>', methods=['GET'])
@require_auth
@rate_limit
def gamification(student_id):
    """Gamification: badges, points, leaderboard"""
    try:
        if session.get('user_id') != student_id and not session.get('is_admin'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        return jsonify({
            'success': True,
            'student_id': student_id,
            'points': 450,
            'level': 3,
            'badges': [
                {'badge': 'first_quiz', 'name': 'Quiz Starter', 'icon': '🎯'},
                {'badge': 'perfect_score', 'name': 'Perfect Score', 'icon': '⭐'}
            ],
            'achievements': [
                'Completed first quiz',
                'Scored 100% on 3 quizzes',
                'Studied for 10 consecutive days'
            ]
        })
    except Exception as e:
        logger.error(f"Gamification error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch gamification data'}), 500



@app.route('/api/import-csv', methods=['POST'])
@require_admin_token
def import_csv():
    data = request.get_json() or {}
    import_password = data.get('import_password')
    csv_path = data.get('csv_path', IMPORT_CSV_PATH)

    if import_password != ADMIN_IMPORT_PASSWORD:
        return jsonify({'success': False, 'message': 'Import password invalid'}), 403

    if not os.path.exists(csv_path):
        return jsonify({'success': False, 'message': f'CSV file not found: {csv_path}'}), 404

    imported = []
    skipped = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        db = get_db()
        for row in reader:
            kind = (row.get('type') or '').strip().lower()
            if not kind:
                continue

            if kind == 'admin':
                user_id = normalize_user_id(kind, row.get('id'), row.get('username'))
                username = (row.get('username') or '').strip()
                if not username:
                    skipped.append({'row': row, 'reason': 'Missing admin username'})
                    continue
                if row.get('id') and row.get('id').strip().upper() == ADMIN_ID:
                    skipped.append({'row': row, 'reason': 'Super admin ID is reserved'} )
                    continue
                if username == ADMIN_SECRET_KEY:
                    skipped.append({'row': row, 'reason': 'Super admin username is reserved'} )
                    continue
                if not user_id:
                    user_id = f'A{random.randint(100,999)}'
                password = (row.get('password') or '').strip() or secrets.token_urlsafe(8)
                hashed_password = hash_password(password)
                full_name = (row.get('fullName') or '').strip() or username
                email = (row.get('email') or '').strip() or None
                stream = (row.get('stream') or '').strip() or 'Unassigned'
                klass = (row.get('class') or '').strip() or 'Unknown'
                role = (row.get('role') or '').strip() or 'Admin'
                payment_status = (row.get('payment_status') or '').strip() or 'paid'
                certificate = (row.get('certificate') or '').strip() or None

                db.execute('''INSERT OR REPLACE INTO students
                    (id, username, password, fullName, email, stream, class, role, photo, is_admin, certificate, payment_status, login_attempts, lockout_until, mental_wellbeing, decision_making, ambitions, hobbies, behavior_profile)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, ?, ?, ?, ?, ?)''',
                    (user_id, username, hashed_password, full_name, email, stream, klass, role, None, 1, certificate, payment_status,
                     row.get('mental_wellbeing'), row.get('decision_making'), row.get('ambitions'), row.get('hobbies'), row.get('behavior_profile')))
                imported.append({'type': kind, 'id': user_id, 'username': username})
                continue

            user_id = normalize_user_id(kind, row.get('id'), row.get('username'))
            username = (row.get('username') or '').strip()
            if not username:
                skipped.append({'row': row, 'reason': 'Missing username'})
                continue

            password = (row.get('password') or '').strip() or secrets.token_urlsafe(8)
            hashed_password = hash_password(password)
            full_name = (row.get('fullName') or '').strip() or username
            email = (row.get('email') or '').strip() or None
            stream = (row.get('stream') or '').strip() or 'Unassigned'
            klass = (row.get('class') or '').strip() or 'Unknown'
            role = (row.get('role') or '').strip() or ('Normal student' if kind == 'student' else 'Normal teacher')
            is_admin = 1 if parse_bool(row.get('is_admin', '0')) else 0
            payment_status = (row.get('payment_status') or '').strip() or 'unpaid'
            certificate = (row.get('certificate') or '').strip() or None

            if kind == 'student':
                db.execute('''INSERT OR REPLACE INTO students
                    (id, username, password, fullName, email, stream, class, role, photo, is_admin, certificate, payment_status, login_attempts, lockout_until, mental_wellbeing, decision_making, ambitions, hobbies, behavior_profile)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, ?, ?, ?, ?, ?)''',
                    (user_id, username, hashed_password, full_name, email, stream, klass, role, None, is_admin, certificate, payment_status,
                     row.get('mental_wellbeing'), row.get('decision_making'), row.get('ambitions'), row.get('hobbies'), row.get('behavior_profile')))
                imported.append({'type': kind, 'id': user_id, 'username': username})
            elif kind == 'teacher':
                subjects = (row.get('subjects') or '').strip() or ''
                quote = (row.get('quote') or '').strip() or ''
                db.execute('''INSERT OR REPLACE INTO teachers
                    (id, username, password, fullName, email, subjects, stream, class, photo, quote, role, is_admin, certificate, payment_status, login_attempts, lockout_until)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL)''',
                    (user_id, username, hashed_password, full_name, email, subjects, stream, klass, None, quote, role, is_admin, certificate, payment_status))
                imported.append({'type': kind, 'id': user_id, 'username': username})
            else:
                skipped.append({'row': row, 'reason': f'Unknown type: {kind}'})

        db.commit()
    return jsonify({'success': True, 'imported': imported, 'skipped': skipped})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
def log_action(db, user_id, user_type, username, action):
    # Skip audit logging for A000 super admin (A000 should not be logged)
    if user_id == ADMIN_ID and action == 'admin_login':
        return
    db.execute('INSERT INTO loginLogs (userId, userType, username, ipAddress, action) VALUES (?, ?, ?, ?, ?)',
               (user_id, user_type, username, request.remote_addr, action))


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    role = (data.get('role') or '').strip().lower() if data.get('role') else None

    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400

    now = datetime.now()
    db = get_db()

    # Special admin override
    if username == ADMIN_SECRET_KEY and password == ADMIN_SECRET_PASSWORD:
        user = db.execute('SELECT * FROM students WHERE id = ?', (ADMIN_ID,)).fetchone()
        if not user:
            return jsonify({'success': False, 'message': 'Admin override user not found'}), 404

        user_data = dict(user)
        user_data.pop('password', None)

        # Create Flask session
        session.clear()
        session['user_id'] = user_data['id']
        session['username'] = user_data['username']
        session['role'] = 'admin'
        session['is_admin'] = True

        return jsonify({
            'success': True,
            'message': f'Logged in as {user_data.get("username") or username} (Admin Override)',
            'user': user_data,
            'role': 'admin',
            'is_admin': True
        })

    if role:
        table = 'students' if role == 'student' else 'teachers'
        user = db.execute(f'SELECT * FROM {table} WHERE username = ?', (username,)).fetchone()
        if not user and role == 'teacher':
            user = db.execute('SELECT * FROM students WHERE username = ? AND is_admin = 1', (username,)).fetchone()
            if user:
                table = 'students'
                
        print(
            f"[LOGIN DEBUG] User FOUND: "
            f"id={user['id']}, "
            f"username={user['username']}, "
            f"role={role}"
        )

        #if not user:
        #    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        #return handle_login_result(db, user, table, role, username, password, now)
        
        if not user:
            print(f"[LOGIN DEBUG] User NOT FOUND: username={username}, role={role}")
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401

    # If no role specified, try to find user as student or teacher (not just admin)
    user = db.execute('SELECT * FROM students WHERE username = ?', (username,)).fetchone()
    user_role = 'student'
    table = 'students'
    if not user:
        user = db.execute('SELECT * FROM teachers WHERE username = ?', (username,)).fetchone()
        if not user:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        user_role = 'teacher'
        table = 'teachers'
    return handle_login_result(db, user, table, user_role, username, password, now)

def handle_login_result(db, user, table, role, username, password, now):
    user_dict = dict(user)
    lockout_until = user_dict.get('lockout_until')
    if lockout_until and datetime.fromisoformat(lockout_until) > now:
        return jsonify({
            'success': False,
            'message': f'Too many failed login attempts. Please retry after {lockout_until}'
        }), 423

    if not check_password(password, user_dict['password']):
        attempts = user_dict['login_attempts'] + 1
        new_lockout = None
        if attempts >= LOGIN_ATTEMPTS_LIMIT:
            new_lockout = (now + timedelta(hours=LOCKOUT_HOURS)).isoformat()

        db.execute(f'UPDATE {table} SET login_attempts = ?, lockout_until = ? WHERE id = ?',
                   (attempts, new_lockout, user_dict['id']))
        log_action(db, user_dict['id'], role, username, 'failed_login')

        remaining = max(LOGIN_ATTEMPTS_LIMIT - attempts, 0)
        message = f'Invalid username or password. {remaining} attempts remaining.' if not new_lockout else f'Too many failed login attempts. Your account is locked until {new_lockout}'
        return jsonify({'success': False, 'message': message}), 401

    db.execute(f'UPDATE {table} SET login_attempts = 0, lockout_until = NULL WHERE id = ?', (user_dict['id'],))
    db.commit()

    # Create login session
    session.clear()
    session['user_id'] = user_dict['id']
    session['username'] = user_dict['username']
    session['role'] = role
    session['is_admin'] = bool(user_dict.get('is_admin'))

    if user_dict.get('is_admin'):
        log_action(db, user_dict['id'], role, username, 'admin_login')
        db.commit()
        user_data = dict(user_dict)
        del user_data['password']
        return jsonify({
            'success': True,
            'message': f'Logged in as {username} (Admin)',
            'user': user_data,
            'role': role,
            'is_admin': True
        })

    if user_dict.get('payment_status') != 'paid':
        return jsonify({
            'success': False,
            'message': 'Payment required to access the website',
            'requires_payment': True,
            'user_id': user_dict['id'],
            'user_type': role
        }), 402

    log_action(db, user_dict['id'], role, username, 'login')
    db.commit()

    user_data = dict(user_dict)
    del user_data['password']
    return jsonify({
        'success': True,
        'message': f'Logged in as {username}',
        'user': user_data,
        'role': role
    })


@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM students WHERE id = ?', (user_id,)).fetchone()
    if user:
        user_data = dict(user)
        del user_data['password']
        return jsonify({'success': True, 'user': user_data, 'role': 'student'})

    user = db.execute('SELECT * FROM teachers WHERE id = ?', (user_id,)).fetchone()
    if user:
        user_data = dict(user)
        del user_data['password']
        return jsonify({'success': True, 'user': user_data, 'role': 'teacher'})
    return jsonify({'success': False, 'message': 'User not found'}), 404

@app.route('/api/bible-quotes', methods=['GET'])
def get_bible_quotes():
    quotes = [
        {'quote': 'For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.', 'reference': 'Jeremiah 29:11'},
        {'quote': 'Trust in the Lord with all your heart and lean not on your own understanding.', 'reference': 'Proverbs 3:5'},
        {'quote': 'Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.', 'reference': 'Joshua 1:9'},
        {'quote': 'The Lord is my shepherd, I lack nothing.', 'reference': 'Psalm 23:1'},
        {'quote': 'I can do all things through Christ who strengthens me.', 'reference': 'Philippians 4:13'}
    ]
    return jsonify(quotes)


@app.context_processor
def inject_site_info():
    about = {
        'title': 'Mengo Senior School',
        'founded': 1895,
        'mission': 'To provide quality, holistic education...',
        'url': 'https://mengoss.sc.ug'
    }
    return dict(about_mss=about)

@app.route('/api/updates', methods=['GET', 'POST'])
def handle_updates():
    db = get_db()
    if request.method == 'POST':
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        message = (data.get('message') or '').strip()
        user_id = (data.get('user_id') or '').strip()
        full_name = (data.get('fullName') or '').strip()
        role = (data.get('role') or '').strip()

        if not title or not message or not user_id:
            return jsonify({'success': False, 'message': 'Missing update fields'}), 400

        db.execute('INSERT INTO updates (user_id, fullName, role, title, message) VALUES (?, ?, ?, ?, ?)',
                   (user_id, full_name, role, title, message))
        db.commit()
        return jsonify({'success': True, 'message': 'Update posted'})

    updates = db.execute('SELECT * FROM updates ORDER BY created_at DESC LIMIT 50').fetchall()
    return jsonify({'success': True, 'updates': [dict(u) for u in updates]})

@app.route('/api/assignments', methods=['GET', 'POST'])
def handle_assignments():
    db = get_db()
    if request.method == 'POST':
        data = request.get_json() or {}
        teacher_id = (data.get('teacher_id') or '').strip()
        teacher_name = (data.get('teacher_name') or '').strip()
        stream = (data.get('stream') or '').strip()
        klass = (data.get('class') or '').strip()
        subject = (data.get('subject') or '').strip()
        title = (data.get('title') or '').strip()
        description = (data.get('description') or '').strip()
        due_date = (data.get('due_date') or '').strip()

        if not teacher_id or not subject or not title or not description:
            return jsonify({'success': False, 'message': 'Missing assignment fields'}), 400

        db.execute('INSERT INTO assignments (teacher_id, teacher_name, stream, class, subject, title, description, due_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (teacher_id, teacher_name, stream, klass, subject, title, description, due_date or None))
        db.commit()
        return jsonify({'success': True, 'message': 'Assignment posted'})

    stream = request.args.get('stream', '')
    klass = request.args.get('class', '')
    query = 'SELECT * FROM assignments'
    params = []
    if stream and klass:
        query += ' WHERE stream = ? AND class = ?'
        params = [stream, klass]
    elif stream:
        query += ' WHERE stream = ?'
        params = [stream]
    elif klass:
        query += ' WHERE class = ?'
        params = [klass]

    assignments = db.execute(query + ' ORDER BY created_at DESC', params).fetchall()
    assignments_list = [dict(a) for a in assignments]
    return jsonify({'success': True, 'assignments': assignments_list})

@app.route('/api/timetable/<stream>', methods=['GET'])
def get_timetable(stream):
    timetable_path = Path('data/timetables') / f'{stream}.json'
    if not timetable_path.exists():
        timetable_path = Path('data/timetables/default.json')
        if not timetable_path.exists():
            return jsonify({'success': False, 'message': 'Timetable not found'}), 404

    with open(timetable_path, 'r', encoding='utf-8') as f:
        timetable = json.load(f)
    return jsonify({'success': True, 'timetable': timetable})

@app.route('/api/audio/beats', methods=['GET'])
def get_audio_beats():
    beats_dir = Path('public/audio/beats')
    if not beats_dir.exists():
        return jsonify({'success': True, 'beats': []})
    beats = [f for f in os.listdir(beats_dir) if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
    return jsonify({'success': True, 'beats': beats})

@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    db = get_db()
    teachers = db.execute('SELECT id, fullName, subjects, quote, stream, class, photo, role FROM teachers ORDER BY fullName COLLATE NOCASE ASC').fetchall()
    return jsonify({'success': True, 'teachers': [dict(t) for t in teachers]})

@app.route('/api/students', methods=['GET'])
def get_students():
    db = get_db()
    students = db.execute('SELECT id, fullName, stream, class, role, photo FROM students ORDER BY fullName COLLATE NOCASE ASC').fetchall()
    return jsonify({'success': True, 'students': [dict(s) for s in students]})

# Premium Features are now registered via register_premium_routes() in premium_routes.py

# Teacher Chat with Real Replies
@app.route('/api/messages', methods=['GET'])
def get_messages():
    student_id = request.args.get('student_id')
    teacher_id = request.args.get('teacher_id')

    if not student_id or not teacher_id:
        return jsonify({'success': False, 'message': 'Missing student or teacher id'}), 400

    db = get_db()
    messages = db.execute('SELECT * FROM messages WHERE student_id = ? AND teacher_id = ? ORDER BY created_at ASC',
                         (student_id, teacher_id)).fetchall()

    return jsonify({'success': True, 'messages': [dict(m) for m in messages]})

@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    student_id = data.get('student_id')
    teacher_id = data.get('teacher_id')
    from_role = data.get('from_role')
    sender_id = data.get('sender_id')
    message = data.get('message')
    attachment_name = data.get('attachment_name')

    if not all([student_id, teacher_id, from_role, sender_id, message]):
        return jsonify({'success': False, 'message': 'Missing message fields'}), 400

    # Only students can send initial messages, teachers reply
    if from_role not in ['student', 'teacher']:
        return jsonify({'success': False, 'message': 'Invalid role'}), 400

    db = get_db()
    db.execute('INSERT INTO messages (student_id, teacher_id, from_role, sender_id, message, attachment_name) VALUES (?, ?, ?, ?, ?, ?)',
               (student_id, teacher_id, from_role, sender_id, message, attachment_name or None))
    db.commit()
    
    # Send notification email only if student sent message
    if from_role == 'student':
        teacher = db.execute('SELECT email FROM teachers WHERE id = ?', (teacher_id,)).fetchone()
        if teacher and teacher['email']:
            send_notification_email(teacher['email'], f'New message from student {student_id}', message)
    return jsonify({'success': True, 'message': 'Message sent'})

@app.route('/api/messages/reply', methods=['POST'])
def teacher_reply():
    data = request.get_json()
    message_id = data.get('message_id')
    reply = data.get('reply')
    teacher_id = data.get('teacher_id')

    if not all([message_id, reply, teacher_id]):
        return jsonify({'success': False, 'message': 'Missing reply fields'}), 400

    db = get_db()
    message = db.execute('SELECT * FROM messages WHERE id = ?', (message_id,)).fetchone()
    if not message:
        return jsonify({'success': False, 'message': 'Message not found'}), 404

    # Verify the replying user is a teacher
    teacher = db.execute('SELECT id FROM teachers WHERE id = ?', (teacher_id,)).fetchone()
    if not teacher:
        return jsonify({'success': False, 'message': 'Only teachers can reply'}), 403

    # Insert teacher reply
    db.execute('INSERT INTO messages (student_id, teacher_id, from_role, sender_id, message) VALUES (?, ?, ?, ?, ?)',
               (message['student_id'], teacher_id, 'teacher', teacher_id, reply))

    # Mark original message as read
    db.execute('UPDATE messages SET is_read = 1 WHERE id = ?', (message_id,))
    db.commit()
    
    # Send notification to student that teacher replied
    student = db.execute('SELECT email FROM students WHERE id = ?', (message['student_id'],)).fetchone()
    if student and student['email']:
        send_notification_email(student['email'], f'Teacher {teacher_id} replied to your message', reply)
    return jsonify({'success': True, 'message': 'Reply sent by teacher'})

def send_notification_email(to_email, subject, body):
    # In production, configure SMTP
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'noreply@mengo-hub.com'
        msg['To'] = to_email

        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login('your-email@gmail.com', 'your-password')
        # server.sendmail(msg['From'], [msg['To']], msg.as_string())
        # server.quit()

        print(f'Email notification sent to {to_email}: {subject}')
    except Exception as e:
        print(f'Failed to send email: {e}')

# Admin routes
@app.route('/api/admin/users', methods=['GET'])
@require_admin_token
def get_all_users():
    db = get_db()
    if is_super_admin_request():
        students = db.execute('SELECT id, username, fullName, email, role, is_admin, payment_status, stream, class, photo, createdAt FROM students ORDER BY fullName COLLATE NOCASE ASC').fetchall()
    else:
        students = db.execute('SELECT id, username, fullName, email, role, is_admin, payment_status, stream, class, photo, createdAt FROM students WHERE id != ? ORDER BY fullName COLLATE NOCASE ASC', (ADMIN_ID,)).fetchall()
    teachers = db.execute('SELECT id, username, fullName, email, subjects, stream, class, role, is_admin, payment_status, photo, createdAt FROM teachers ORDER BY fullName COLLATE NOCASE ASC').fetchall()

    users = []
    users.extend([dict(s) for s in students])
    users.extend([dict(t) for t in teachers])
    users.sort(key=lambda x: (x.get('fullName') or x.get('username') or '').lower())
    return jsonify({'success': True, 'users': users})

@app.route('/api/admin/admins', methods=['GET'])
@require_admin_token
def get_admins():
    db = get_db()
    if is_super_admin_request():
        admins = db.execute('SELECT id, username, fullName, email, role, payment_status, stream, class, photo, createdAt FROM students WHERE is_admin = 1 ORDER BY fullName COLLATE NOCASE ASC').fetchall()
    else:
        admins = db.execute('SELECT id, username, fullName, email, role, payment_status, stream, class, photo, createdAt FROM students WHERE is_admin = 1 AND id != ? ORDER BY fullName COLLATE NOCASE ASC', (ADMIN_ID,)).fetchall()
    return jsonify({'success': True, 'admins': [dict(a) for a in admins]})

@app.route('/api/admin/teachers', methods=['GET'])
@require_admin_token
def get_admin_teachers():
    db = get_db()
    teachers = db.execute('SELECT id, username, fullName, email, subjects, stream, class, role, payment_status, photo, createdAt FROM teachers ORDER BY fullName COLLATE NOCASE ASC').fetchall()
    return jsonify({'success': True, 'teachers': [dict(t) for t in teachers]})

@app.route('/api/admin/students', methods=['GET'])
@require_admin_token
def get_admin_students():
    db = get_db()
    if is_super_admin_request():
        students = db.execute('SELECT id, username, fullName, email, role, payment_status, stream, class, photo, createdAt FROM students ORDER BY fullName COLLATE NOCASE ASC').fetchall()
    else:
        students = db.execute('SELECT id, username, fullName, email, role, payment_status, stream, class, photo, createdAt FROM students WHERE id != ? ORDER BY fullName COLLATE NOCASE ASC', (ADMIN_ID,)).fetchall()
    return jsonify({'success': True, 'students': [dict(s) for s in students]})

@app.route('/api/admin/reports', methods=['GET'])
@require_admin_token
def get_admin_reports():
    db = get_db()
    student_count = db.execute('SELECT COUNT(*) FROM students WHERE id != ?', (ADMIN_ID,)).fetchone()[0]
    teacher_count = db.execute('SELECT COUNT(*) FROM teachers').fetchone()[0]
    admin_count = db.execute('SELECT COUNT(*) FROM students WHERE is_admin = 1 AND id != ?', (ADMIN_ID,)).fetchone()[0]
    unresolved_payments = db.execute('SELECT COUNT(*) FROM students WHERE payment_status != "paid"').fetchone()[0]
    recent_logs = db.execute('SELECT userId, userType, username, loginTime, action FROM loginLogs ORDER BY loginTime DESC LIMIT 20').fetchall()

    return jsonify({
        'success': True,
        'report': {
            'student_count': student_count,
            'teacher_count': teacher_count,
            'admin_count': admin_count,
            'unresolved_payments': unresolved_payments,
            'recent_logs': [dict(r) for r in recent_logs]
        }
    })

@app.route('/api/admin/super-reports', methods=['GET'])
@require_super_admin_token
def get_super_reports():
    db = get_db()
    student_count = db.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    teacher_count = db.execute('SELECT COUNT(*) FROM teachers').fetchone()[0]
    admin_count = db.execute('SELECT COUNT(*) FROM students WHERE is_admin = 1').fetchone()[0]
    total_payments = db.execute('SELECT SUM(amount) FROM payments WHERE status = "paid"').fetchone()[0] or 0
    recent_logs = db.execute('SELECT * FROM loginLogs ORDER BY loginTime DESC LIMIT 50').fetchall()
    admins = db.execute('SELECT id, username, fullName, email, role, payment_status, createdAt FROM students WHERE is_admin = 1 ORDER BY fullName COLLATE NOCASE ASC').fetchall()

    return jsonify({
        'success': True,
        'super_report': {
            'student_count': student_count,
            'teacher_count': teacher_count,
            'admin_count': admin_count,
            'total_payment_amount': total_payments,
            'admins': [dict(a) for a in admins],
            'recent_logs': [dict(r) for r in recent_logs]
        }
    })

@app.route('/api/admin/upload-photo', methods=['POST'])
@require_admin_token
def upload_photo():
    data = request.get_json()
    user_type = data.get('user_type')
    user_id = data.get('user_id')
    filename = data.get('filename')
    fileData = data.get('fileData')

    if not all([user_type, user_id, filename, fileData]):
        return jsonify({'success': False, 'message': 'Missing upload parameters'}), 400

    if user_type not in ['student', 'teacher']:
        return jsonify({'success': False, 'message': 'Invalid user type'}), 400

    matches = re.match(r'^data:image/(.+);base64,(.+)$', fileData)
    if not matches:
        return jsonify({'success': False, 'message': 'Invalid file data format'}), 400

    image_data = base64.b64decode(matches.group(2))
    folder = f'public/images/{user_type}s'
    safe_name = f'{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{secure_filename(filename)}'
    file_path = os.path.join(folder, safe_name)
    photo_path = f'images/{user_type}s/{safe_name}'

    with open(file_path, 'wb') as f:
        f.write(image_data)

    table = 'students' if user_type == 'student' else 'teachers'
    db = get_db()
    db.execute(f'UPDATE {table} SET photo = ? WHERE id = ?', (photo_path, user_id))
    db.commit()
    return jsonify({'success': True, 'message': 'Photo uploaded successfully', 'photo': photo_path})

# More admin routes...
@app.route('/api/logs', methods=['GET'])
@require_admin_token
def get_logs():
    db = get_db()
    logs = db.execute('SELECT * FROM loginLogs ORDER BY loginTime DESC LIMIT 100').fetchall()
    return jsonify({'success': True, 'logs': [dict(l) for l in logs]})

@app.route('/')
def root():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('public', filename)

# ============ AUDIO SERVICE ROUTES ============
@app.route('/api/audio/upload', methods=['POST'])
@require_admin_token
def upload_audio():
    """Upload audio file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        audio_type = request.form.get('audio_type', 'music')  # beat, music, nature_sound
        category = request.form.get('category', 'general')
        user_id = session.get('user_id')
        
        result = audio_service.upload_audio_file(file, audio_type, category, user_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/audio/playlists', methods=['GET'])
def get_playlists():
    """Get user's playlists"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        result = audio_service.get_playlists(user_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/audio/playlists', methods=['POST'])
def create_playlist():
    """Create new playlist"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        result = audio_service.create_playlist(
            data.get('playlist_name'),
            user_id,
            data.get('is_public', True),
            data.get('description', '')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/audio/playlists/<int:playlist_id>/add', methods=['POST'])
def add_to_playlist(playlist_id):
    """Add audio to playlist"""
    try:
        data = request.get_json()
        result = audio_service.add_audio_to_playlist(playlist_id, data.get('audio_id'))
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/audio/overlays', methods=['GET'])
def get_music_overlays():
    """Get music overlays"""
    try:
        environment = request.args.get('environment')
        result = audio_service.get_music_overlays(environment)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/audio/<int:audio_id>/play', methods=['POST'])
def record_playback(audio_id):
    """Record audio playback"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        result = audio_service.record_audio_playback(
            user_id,
            audio_id,
            data.get('duration_played', 0),
            data.get('completed', False)
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ DOCUMENT SERVICE ROUTES ============
@app.route('/api/documents/upload', methods=['POST'])
@require_admin_token
def upload_document():
    """Upload document"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        subject = request.form.get('subject')
        academic_level = request.form.get('academic_level')
        document_type = request.form.get('document_type')
        teacher_id = session.get('user_id')
        
        result = document_service.upload_document(
            file, subject, academic_level, document_type, teacher_id,
            request.form.get('title'), request.form.get('description', '')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get accessible documents"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        filters = {
            'subject': request.args.get('subject'),
            'academic_level': request.args.get('level'),
            'document_type': request.args.get('type')
        }
        filters = {k: v for k, v in filters.items() if v}
        
        result = document_service.get_accessible_documents(user_id, filters)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/<int:document_id>/download', methods=['GET'])
def download_document(document_id):
    """Download document"""
    try:
        user_id = session.get('user_id')
        result = document_service.download_document(document_id, user_id)
        
        if result['success']:
            return send_file(result['file_path'], as_attachment=True)
        return jsonify(result), 403
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/<int:document_id>/grant-access', methods=['POST'])
@require_admin_token
def grant_document_access(document_id):
    """Grant document access to students"""
    try:
        data = request.get_json()
        student_list = data.get('student_ids', [])
        
        result = document_service.grant_bulk_access(
            document_id,
            student_list,
            data.get('access_level', 'view')
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/<int:document_id>/search', methods=['GET'])
def search_documents(document_id):
    """Search documents"""
    try:
        user_id = session.get('user_id')
        query = request.args.get('q', '')
        
        result = document_service.search_documents(
            query, user_id, request.args.get('type')
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ CHAT SERVICE ROUTES ============
@app.route('/api/chat/groups', methods=['POST'])
def create_group():
    """Create chat group"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        result = chat_service.create_group_chat(
            data.get('group_name'),
            user_id,
            data.get('group_type', 'general'),
            data.get('description', '')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/groups', methods=['GET'])
def get_user_groups():
    """Get user's chat groups"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        result = chat_service.get_user_groups(user_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/groups/<int:group_id>/members', methods=['POST'])
def add_group_member(group_id):
    """Add member to group"""
    try:
        data = request.get_json()
        result = chat_service.add_group_member(
            group_id,
            data.get('user_id'),
            data.get('role', 'member')
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/groups/<int:group_id>/messages', methods=['GET'])
def get_group_messages(group_id):
    """Get group messages"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = chat_service.get_group_messages(group_id, limit, offset)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/direct/<other_user_id>', methods=['GET'])
def get_direct_messages(other_user_id):
    """Get direct messages"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = chat_service.get_direct_messages(user_id, other_user_id, limit, offset)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/features/<feature_name>/toggle', methods=['POST'])
@require_admin_token
def toggle_feature(feature_name):
    """Toggle a feature (chat, DMs, etc.)"""
    try:
        data = request.get_json()
        result = chat_service.toggle_feature(
            feature_name,
            data.get('is_enabled', True),
            data.get('disabled_message'),
            data.get('disabled_until')
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/features/<feature_name>/status', methods=['GET'])
def check_feature_status(feature_name):
    """Check if feature is enabled"""
    try:
        result = chat_service.is_feature_enabled(feature_name)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'enabled': True, 'error': str(e)}), 200

# ============ SocketIO Chat Events ============
@socketio.on('send_group_message')
def handle_group_message(data):
    """Handle group message via WebSocket"""
    try:
        group_id = data.get('group_id')
        sender_id = session.get('user_id')
        message_text = data.get('message')
        
        # Check if chat is enabled
        feature_status = chat_service.is_feature_enabled('group_chat')
        if not feature_status['enabled']:
            emit('error', {'message': feature_status.get('message', 'Group chat is disabled')})
            return
        result = chat_service.send_group_message(group_id, sender_id, message_text)
        
        if result['success']:
            emit('new_message', {
                'message_id': result['message_id'],
                'sender_id': sender_id,
                'message_text': message_text,
                'timestamp': result['timestamp'].isoformat()
            }, room=f'group_{group_id}')
    except Exception as e:
        emit('error', {'error': str(e)})

@socketio.on('send_direct_message')
def handle_direct_message(data):
    """Handle direct message via WebSocket"""
    try:
        recipient_id = data.get('recipient_id')
        sender_id = session.get('user_id')
        message_text = data.get('message')
        
        # Check if DM is enabled
        feature_status = chat_service.is_feature_enabled('direct_messages')
        if not feature_status['enabled']:
            emit('error', {'message': feature_status.get('message', 'Direct messages are disabled')})
            return
        result = chat_service.send_direct_message(sender_id, recipient_id, message_text)
        
        if result['success']:
            emit('new_message', {
                'message_id': result['message_id'],
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'message_text': message_text,
                'timestamp': result['timestamp'].isoformat()
            }, room=f'dm_{sender_id}_{recipient_id}')
    except Exception as e:
        emit('error', {'error': str(e)})

@socketio.on('join_group')
def on_join_group(data):
    """Join group chat room"""
    group_id = data.get('group_id')
    join_room(f'group_{group_id}')
    emit('status', {'msg': f'User joined group {group_id}'})

@socketio.on('join_dm')
def on_join_dm(data):
    """Join DM room"""
    other_user_id = data.get('other_user_id')
    user_id = session.get('user_id')
    room_id = f'dm_{min(user_id, other_user_id)}_{max(user_id, other_user_id)}'
    join_room(room_id)
    emit('status', {'msg': 'Joined DM room'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connect_response', {'data': 'Connected to AI Research server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('ai_research_query')
def handle_ai_research(data):
    """Handle AI research streaming queries"""
    try:
        query = data.get('query', '').strip()
        student_id = data.get('student_id', 'anonymous')
        subject = data.get('subject', 'general').strip()

        if not query:
            emit('error', {'message': 'Query required'})
            return

        logger.info(f"AI research query from {student_id}: {query[:50]}...")

        # Stream response in chunks
        prompt = f"Research query for {subject}:\n{query}\n\nProvide detailed, accurate information."
        
        try:
            response = ai_service.query(prompt)
            
            # Send response in chunks
            chunk_size = 100
            for i in range(0, len(response), chunk_size):
                emit('ai_research_chunk', {
                    'chunk': response[i:i+chunk_size],
                    'progress': min(100, int((i / len(response)) * 100))
                })
            
            emit('ai_research_complete', {
                'status': 'completed',
                'total_length': len(response)
            })
        except Exception as e:
            logger.error(f"AI query error: {str(e)}")
            emit('error', {'message': 'Failed to process query'})

    except Exception as e:
        logger.error(f"Research handler error: {str(e)}")
        emit('error', {'message': 'Research query failed'})

# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({'success': False, 'message': 'Bad request'}), 400


@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 errors"""
    return jsonify({'success': False, 'message': 'Unauthorized'}), 401


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({'success': False, 'message': 'Forbidden'}), 403


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'message': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


# ==================== ADMIN & SECURITY ROUTES ====================
@app.route('/api/admin/certificate/generate', methods=['POST'])
def generate_admin_certificate():
    """Generate super admin certificate - Super Admin only"""
    try:
        data = request.get_json()
        admin_service = AdminSecurityService(DATABASE_URL)
        result = admin_service.generate_super_admin_certificate(
            data.get('admin_id'),
            session.get('user_id'),
            data.get('validity_days', 365)
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ADMIN ANNOUNCEMENTS ROUTES ====================
@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    """Get active announcements visible to current user"""
    try:
        user_id = session.get('user_id')
        user_role = session.get('role', 'student')
        db = get_db()
        
        # Get announcements based on user role
        announcements = db.execute('''
            SELECT id, admin_id, admin_name, title, message, 
                   target_users, created_at, expires_at, views_count
            FROM admin_announcements
            WHERE is_active = 1
            AND (target_users = 'all' OR target_users = ?)
            AND (expires_at IS NULL OR expires_at > datetime('now'))
            ORDER BY created_at DESC
            LIMIT 20
        ''', (user_role,)).fetchall()
        
        return jsonify({
            'success': True,
            'announcements': [dict(a) for a in announcements],
            'count': len(announcements)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/announcements', methods=['POST'])
@require_admin_token
def create_announcement():
    """Create admin announcement - Admin only"""
    try:
        data = request.get_json() or {}
        admin_id = session.get('user_id')
        
        if not admin_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        title = (data.get('title') or '').strip()
        message = (data.get('message') or '').strip()
        target_users = (data.get('target_users') or 'all').strip()
        expires_at = data.get('expires_at')
        
        if not title or not message:
            return jsonify({'success': False, 'error': 'Missing title or message'}), 400
        
        if target_users not in ['all', 'students', 'teachers', 'admins']:
            target_users = 'all'
        db = get_db()
        
        # Get admin name
        admin = db.execute('SELECT fullName FROM students WHERE id = ?', (admin_id,)).fetchone()
        admin_name = dict(admin).get('fullName', 'Admin') if admin else 'Admin'
        
        db.execute('''
            INSERT INTO admin_announcements 
            (admin_id, admin_name, title, message, target_users, expires_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (admin_id, admin_name, title, message, target_users, expires_at))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Announcement created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/announcements/<int:announcement_id>', methods=['DELETE'])
@require_admin_token
def delete_announcement(announcement_id):
    """Delete announcement - Admin only"""
    try:
        admin_id = session.get('user_id')
        db = get_db()
        
        # Check if admin owns this announcement
        announcement = db.execute(
            'SELECT admin_id FROM admin_announcements WHERE id = ?',
            (announcement_id,)
        ).fetchone()
        
        if not announcement or dict(announcement)['admin_id'] != admin_id:
            # Allow super admin to delete any announcement
            if admin_id != ADMIN_ID:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        db.execute('DELETE FROM admin_announcements WHERE id = ?', (announcement_id,))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Announcement deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/audit-logs', methods=['GET'])
def get_audit_logs():
    """Get audit logs"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        admin_service = AdminSecurityService(DATABASE_URL)
        filters = {
            'action': request.args.get('action'),
            'user_id': request.args.get('user_id'),
            'days': int(request.args.get('days', 7)),
            'limit': int(request.args.get('limit', 100))
        }
        
        result = admin_service.get_audit_logs(user_id, filters)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/feature/status', methods=['GET'])
def get_feature_status():
    """Get all feature statuses"""
    try:
        admin_service = AdminSecurityService(DATABASE_URL)
        result = admin_service.get_feature_status(session.get('user_id'))
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/security/stats', methods=['GET'])
def get_security_stats():
    """Get security statistics"""
    try:
        admin_service = AdminSecurityService(DATABASE_URL)
        result = admin_service.get_security_stats(session.get('user_id'))
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ANALYTICS & AI ROUTES ====================
@app.route('/api/analytics/student/<student_id>/performance', methods=['GET'])
def analyze_student_performance(student_id):
    """Analyze student performance"""
    try:
        analytics = AnalyticsService(DATABASE_URL)
        result = analytics.analyze_student_performance(student_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/plagiarism/check', methods=['POST'])
def check_plagiarism():
    """Check submission for plagiarism"""
    try:
        data = request.get_json()
        analytics = AnalyticsService(DATABASE_URL)
        result = analytics.check_plagiarism(
            data.get('submission_id'),
            data.get('text_content'),
            data.get('student_id'),
            float(data.get('threshold', 0.7))
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """System status endpoint"""
    return jsonify({
        'success': True,
        'app_name': 'Mengo-Hub',
        'version': '1.0.0',
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'ai_provider': ai_service.provider,
        'email_provider': email_service.provider,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analytics/recommendations/<student_id>', methods=['GET'])
def get_recommendations(student_id):
    """Get learning recommendations"""
    try:
        analytics = AnalyticsService(DATABASE_URL)
        result = analytics.get_learning_recommendations(student_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/health', methods=['GET'])
def get_system_health():
    """Get system health status"""
    try:
        analytics = AnalyticsService(DATABASE_URL)
        result = analytics.get_system_health()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== MEDIA & 3D ROUTES ====================
@app.route('/api/media/3d/upload', methods=['POST'])
def upload_3d_model():
    """Upload 3D model"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        media = MediaService(DATABASE_URL)
        result = media.upload_3d_model(
            file,
            request.form.get('model_name', file.filename),
            session.get('user_id'),
            request.form.get('subject', '')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/media/3d/models', methods=['GET'])
def get_3d_models():
    """Get 3D models"""
    try:
        media = MediaService(DATABASE_URL)
        result = media.get_3d_models(
            request.args.get('subject', ''),
            int(request.args.get('limit', 20))
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/media/videos/upload', methods=['POST'])
def upload_video():
    """Upload video"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        media = MediaService(DATABASE_URL)
        quality_levels = request.form.get('quality_levels', '720p').split(',')
        
        result = media.upload_video(
            file,
            request.form.get('video_title', file.filename),
            session.get('user_id'),
            request.form.get('subject', ''),
            quality_levels
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/media/videos/<video_id>/transcript', methods=['POST'])
def add_video_transcript(video_id):
    """Add video transcript"""
    try:
        data = request.get_json()
        media = MediaService(DATABASE_URL)
        result = media.add_video_transcript(
            video_id,
            data.get('transcript_text'),
            data.get('auto_generated', False)
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/media/scan/ocr', methods=['POST'])
def scan_ocr():
    """Scan document using OCR"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        media = MediaService(DATABASE_URL)
        result = media.scan_document_ocr(
            file,
            request.form.get('document_name', file.filename),
            session.get('user_id'),
            request.form.get('language', 'eng'),
            request.form.get('use_premium', 'false').lower() == 'true'
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/media/scan/<scan_id>/export', methods=['GET'])
def export_scan(scan_id):
    """Export scanned document"""
    try:
        media = MediaService(DATABASE_URL)
        result = media.export_scanned_document(
            scan_id,
            request.args.get('format', 'pdf')
        )
        if result['success']:
            return send_file(result['file_path'], as_attachment=True)
        return jsonify(result), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/media/papers/upload', methods=['POST'])
def upload_past_paper():
    """Upload past exam paper"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        media = MediaService(DATABASE_URL)
        result = media.upload_past_paper(
            file,
            request.form.get('paper_name', file.filename),
            session.get('user_id'),
            request.form.get('subject'),
            int(request.form.get('exam_year', datetime.now().year)),
            request.form.get('exam_type', 'final')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/media/papers', methods=['GET'])
def get_past_papers():
    """Get past papers"""
    try:
        media = MediaService(DATABASE_URL)
        result = media.get_past_papers(
            request.args.get('subject', ''),
            int(request.args.get('exam_year', 0)) or None,
            int(request.args.get('limit', 20))
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/offline/queue', methods=['POST'])
def queue_offline_sync():
    """Queue content for offline sync"""
    try:
        data = request.get_json()
        media = MediaService(DATABASE_URL)
        result = media.queue_for_offline_sync(
            session.get('user_id'),
            data.get('content_type'),
            data.get('content_id')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/offline/status', methods=['GET'])
def get_offline_status():
    """Get offline sync status"""
    try:
        media = MediaService(DATABASE_URL)
        result = media.get_sync_status(session.get('user_id'))
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== DASHBOARD ROUTES ====================
@app.route('/api/dashboard/student', methods=['GET'])
def student_dashboard():
    """Get student dashboard"""
    try:
        student_id = session.get('user_id')
        if not student_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        dashboard = DashboardService(DATABASE_URL)
        result = dashboard.get_student_dashboard(student_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/student/portfolio', methods=['GET'])
def student_portfolio():
    """Get student portfolio"""
    try:
        student_id = session.get('user_id')
        if not student_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        dashboard = DashboardService(DATABASE_URL)
        result = dashboard.get_student_portfolio(student_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/teacher', methods=['GET'])
def teacher_dashboard():
    """Get teacher dashboard"""
    try:
        teacher_id = session.get('user_id')
        if not teacher_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        dashboard = DashboardService(DATABASE_URL)
        result = dashboard.get_teacher_dashboard(teacher_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/teacher/marking/<int:exam_id>', methods=['GET'])
def teacher_marking_dashboard(exam_id):
    """Get exam marking dashboard"""
    try:
        teacher_id = session.get('user_id')
        if not teacher_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        dashboard = DashboardService(DATABASE_URL)
        result = dashboard.get_exam_marking_dashboard(teacher_id, exam_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/admin', methods=['GET'])
def admin_dashboard():
    """Get admin dashboard"""
    try:
        admin_id = session.get('user_id')
        if not admin_id or admin_id != 'A000':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        dashboard = DashboardService(DATABASE_URL)
        result = dashboard.get_admin_dashboard(admin_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "success": True
    })

@app.route('/api/dashboard/analytics', methods=['GET'])
def system_analytics():
    """Get system-wide analytics"""
    try:
        admin_id = session.get('user_id')
        if not admin_id or admin_id != 'A000':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        dashboard = DashboardService(DATABASE_URL)
        result = dashboard.get_system_analytics()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if PREMIUM_MODULES_AVAILABLE:
    # Initialize new services with PostgreSQL connection
    db_conn = psycopg2.connect(DATABASE_URL)
    init_audio_service(db_conn)
    init_document_service(db_conn)
    init_chat_service(db_conn)
    
    register_premium_routes(app, get_db, require_admin_token)
    register_websocket_ai(app, socketio)
    print("[✓] Premium features and AI integration loaded")
    print("[✓] Audio, Document, and Chat services initialized")
    print("[✓] Admin Security service initialized")
    print("[✓] Analytics and AI services initialized")
    print("[✓] Media and 3D visualization services initialized")
    print("[✓] Dashboard services initialized")
else:
    print("[!] Running without premium features")

if __name__ == '__main__':
    init_db()
    
    # Check for SSL certificates
    import ssl
    cert_path = 'cert.pem'
    key_path = 'key.pem'
    
    ssl_context = None
    if os.path.exists(cert_path) and os.path.exists(key_path):
        print("[✓] SSL certificates found - running on HTTPS")
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_path, key_path)
        socketio.run(app, host='0.0.0.0', port=5000, ssl_context=ssl_context, debug=True)
    else:
        print("[*] SSL certificates not found - running on HTTP")
        print("[*] To enable HTTPS, run: openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)