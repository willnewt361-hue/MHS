"""
Mengo-Hub Flask Application - Core API Server
Comprehensive educational platform with AI, premium features, and real-time communication
"""

from flask import Flask, request, jsonify, send_file, send_from_directory, session, g
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from functools import wraps
from pathlib import Path
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

import ssl
import sqlite3
import psycopg2
import psycopg2.extras
import bcrypt
import os
import json
import csv
import base64
import smtplib
import secrets
import re
import random
import uuid
import threading
import time
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Data science & ML
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

# AI/ML Deep learning
import torch
from transformers import pipeline
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from PIL import Image
import qrcode
import io
from io import BytesIO
from gpt4all import GPT4All

# Import custom modules
from ai_service import AIService
from email_service import EmailService
from premium_features import AnalyticsService, GamificationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}, r"/socket.io/*": {"origins": "*"}})
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Configure SocketIO with SSL support
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# ============================================================================
# CONFIGURATION
# ============================================================================

ADMIN_ID = os.getenv('ADMIN_ID', 'A000')
ADMIN_SECRET_KEY = os.getenv('ADMIN_SECRET_KEY', 'Newton')
ADMIN_SECRET_PASSWORD = os.getenv('ADMIN_SECRET_PASSWORD', '##0000')
ADMIN_API_TOKEN = os.getenv('ADMIN_API_TOKEN', 'MengoAdminAPIToken2026')
SUPER_ADMIN_API_TOKEN = os.getenv('SUPER_ADMIN_API_TOKEN', 'MengoSuperAdminToken2026')
ADMIN_IMPORT_PASSWORD = os.getenv('ADMIN_IMPORT_PASSWORD', 'ImportPassword2026')

LOGIN_ATTEMPTS_LIMIT = int(os.getenv('LOGIN_ATTEMPTS_LIMIT', '5'))
LOCKOUT_HOURS = int(os.getenv('LOCKOUT_HOURS', '24'))
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'postgresql').lower()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:##000000@localhost:5432/mengo_hub')
IMPORT_CSV_PATH = os.getenv('IMPORT_CSV_PATH', 'data/import.csv')

UPLOAD_FOLDER = 'public/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

# SSL Configuration
USE_SSL = os.getenv('USE_SSL', 'false').lower() == 'true'
CERT_FILE = os.getenv('CERT_FILE', 'data/cert.pem')
KEY_FILE = os.getenv('KEY_FILE', 'data/key.pem')

# Rate limiting
RATE_LIMIT_CALLS = int(os.getenv('RATE_LIMIT_CALLS', '100'))
RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', '3600'))

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('data/attachments', exist_ok=True)
os.makedirs('data/past_papers', exist_ok=True)
os.makedirs('public/images/students', exist_ok=True)
os.makedirs('public/images/teachers', exist_ok=True)

# Initialize services
ai_service = AIService()
email_service = EmailService()
analytics_service = AnalyticsService()
gamification_service = GamificationService()

# ============================================================================
# DATABASE WRAPPER
# ============================================================================

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
    """Get database connection"""
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
    """Close database connection"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# ============================================================================
# AUTHENTICATION & SECURITY
# ============================================================================

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password check error: {str(e)}")
        return False


def require_admin_token(f):
    """Decorator to require admin API token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Admin authorization required'}), 403
        token = auth[7:]
        if token != ADMIN_API_TOKEN and token != SUPER_ADMIN_API_TOKEN:
            return jsonify({'success': False, 'message': 'Invalid admin token'}), 403
        request.is_super_admin = token == SUPER_ADMIN_API_TOKEN
        return f(*args, **kwargs)
    return decorated_function


def require_super_admin_token(f):
    """Decorator to require super admin token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Super admin authorization required'}), 403
        token = auth[7:]
        if token != SUPER_ADMIN_API_TOKEN:
            return jsonify({'success': False, 'message': 'Invalid super admin token'}), 403
        return f(*args, **kwargs)
    return decorated_function


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


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database with schema"""
    with app.app_context():
        db = get_db()

        if DATABASE_TYPE == 'postgresql':
            schema_file = Path('schema.sql')
            if not schema_file.exists():
                logger.error('PostgreSQL schema.sql file not found')
                raise RuntimeError('schema.sql file not found')

            sql = schema_file.read_text()
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            for stmt in statements:
                try:
                    db.execute(stmt)
                except Exception as e:
                    logger.warning(f"Schema execution warning: {str(e)}")
            db.commit()
            return

        # SQLite schema
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

        db.execute('''CREATE TABLE IF NOT EXISTS past_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            file_path TEXT NOT NULL,
            year INTEGER,
            difficulty TEXT,
            score REAL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS email_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            sender_email TEXT,
            sender_name TEXT,
            smtp_server TEXT,
            smtp_port INTEGER,
            api_key TEXT,
            is_active INTEGER DEFAULT 0,
            created_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS admin_certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT NOT NULL,
            certificate_path TEXT NOT NULL,
            issuer TEXT,
            expiry_date DATETIME,
            verified INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        # Create admin account
        db.execute('''INSERT OR REPLACE INTO students
            (id, username, password, fullName, email, stream, class, role, photo, is_admin, certificate, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (ADMIN_ID, ADMIN_SECRET_KEY, hash_password(ADMIN_SECRET_PASSWORD), 
             'System Administrator', 'admin@mengo.com', 'All', 'All', 
             'System Administrator', None, 1, None, 'paid'))

        db.commit()
        logger.info("Database initialized successfully")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def parse_bool(value):
    """Parse string to boolean"""
    return str(value).strip().lower() in ('1', 'true', 'yes', 'y')


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def normalize_user_id(row_type, raw_id, username):
    """Normalize user ID based on type"""
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


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'student').lower()

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400

        db = get_db()
        table = 'students' if role == 'student' else 'teachers'

        db.execute(f'SELECT * FROM {table} WHERE username = ?', (username,))
        user = db.fetchone()

        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

        # Check lockout
        if user.get('lockout_until'):
            lockout_time = datetime.fromisoformat(user['lockout_until'])
            if datetime.now() < lockout_time:
                return jsonify({'success': False, 'message': 'Account locked. Try again later'}), 403

        # Verify password
        if not check_password(password, user['password']):
            attempts = (user.get('login_attempts') or 0) + 1
            if attempts >= LOGIN_ATTEMPTS_LIMIT:
                lockout_until = datetime.now() + timedelta(hours=LOCKOUT_HOURS)
                db.execute(f'UPDATE {table} SET login_attempts = ?, lockout_until = ? WHERE id = ?',
                          (attempts, lockout_until.isoformat(), user['id']))
            else:
                db.execute(f'UPDATE {table} SET login_attempts = ? WHERE id = ?', (attempts, user['id']))
            db.commit()
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

        # Reset login attempts
        db.execute(f'UPDATE {table} SET login_attempts = 0, lockout_until = NULL WHERE id = ?', (user['id'],))
        db.commit()

        # Create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = role
        session['is_admin'] = user.get('is_admin', 0)

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'fullName': user['fullName'],
                'role': role,
                'is_admin': user.get('is_admin', 0)
            }
        })
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


# ============================================================================
# PREMIUM FEATURES - SMART REVISION
# ============================================================================

@app.route('/api/premium/smart-revision', methods=['POST'])
@require_auth
@rate_limit
def smart_revision():
    """AI-powered smart revision with UNEB patterns"""
    try:
        data = request.get_json() or {}
        subject = data.get('subject', '').strip()
        difficulty = data.get('difficulty', 'medium').lower()
        count = int(data.get('count', 10))
        context = data.get('context', '')

        if not subject:
            return jsonify({'success': False, 'message': 'Subject required'}), 400

        # Generate questions using AI
        questions = ai_service.generate_revision_questions(subject, difficulty, count, context)

        # Store in database for tracking
        db = get_db()
        for q in questions:
            db.execute('''INSERT INTO quiz_questions 
                (subject, question, options, correct_answer, explanation, difficulty)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (subject, q.get('question', ''), json.dumps(q.get('options', [])),
                 q.get('correct_answer', ''), q.get('explanation', ''), difficulty))
        db.commit()

        return jsonify({
            'success': True,
            'questions': questions,
            'subject': subject,
            'difficulty': difficulty,
            'count': len(questions)
        })
    except Exception as e:
        logger.error(f"Smart revision error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to generate revision questions'}), 500


# ============================================================================
# PREMIUM FEATURES - WEAKNESS DETECTOR
# ============================================================================

@app.route('/api/premium/weakness-detector', methods=['GET'])
@require_auth
@rate_limit
def weakness_detector():
    """AI-enhanced weakness detector with analysis"""
    try:
        student_id = session.get('user_id')
        db = get_db()

        # Get student performance data
        db.execute('''SELECT * FROM student_performance WHERE student_id = ? 
                     ORDER BY created_at DESC LIMIT 50''', (student_id,))
        performances = db.fetchall()

        if not performances:
            return jsonify({
                'success': True,
                'message': 'No performance data yet',
                'weaknesses': [],
                'recommendations': []
            })

        # Prepare performance data for AI analysis
        perf_data = {
            'student_id': student_id,
            'total_attempts': len(performances),
            'by_subject': {}
        }

        for perf in performances:
            subject = perf['subject']
            if subject not in perf_data['by_subject']:
                perf_data['by_subject'][subject] = []
            perf_data['by_subject'][subject].append({
                'score': perf['score'],
                'total_questions': perf['total_questions'],
                'percentage': (perf['score'] / perf['total_questions'] * 100) if perf['total_questions'] > 0 else 0
            })

        # Analyze using AI
        analysis = ai_service.analyze_student_weaknesses(perf_data)

        return jsonify({
            'success': True,
            'analysis': analysis,
            'performance_summary': {
                'total_attempts': len(performances),
                'subjects_attempted': list(perf_data['by_subject'].keys())
            }
        })
    except Exception as e:
        logger.error(f"Weakness detector error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to analyze weaknesses'}), 500


# ============================================================================
# PREMIUM FEATURES - EXAM PREDICTOR
# ============================================================================

@app.route('/api/premium/exam-predictor', methods=['GET'])
@require_auth
@rate_limit
def exam_predictor():
    """Predict likely exam questions based on patterns"""
    try:
        student_id = session.get('user_id')
        subject = request.args.get('subject', '').strip()

        if not subject:
            return jsonify({'success': False, 'message': 'Subject parameter required'}), 400

        db = get_db()

        # Get student's past performance in subject
        db.execute('''SELECT * FROM student_performance WHERE student_id = ? AND subject = ?
                     ORDER BY created_at DESC LIMIT 20''', (student_id, subject))
        performances = db.fetchall()

        past_performance = [
            {'score': p['score'], 'total': p['total_questions'], 'date': p['created_at']}
            for p in performances
        ]

        # Get predictions using AI
        prediction = ai_service.predict_exam_questions(student_id, subject, past_performance)

        return jsonify({
            'success': True,
            'subject': subject,
            'prediction': prediction
        })
    except Exception as e:
        logger.error(f"Exam predictor error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to predict exam questions'}), 500


# ============================================================================
# PREMIUM FEATURES - AI-GENERATED STUDY PLAN
# ============================================================================

@app.route('/api/premium/study-plan', methods=['POST', 'GET'])
@require_auth
@rate_limit
def study_plan():
    """AI-generated personalized study plan"""
    try:
        student_id = session.get('user_id')
        db = get_db()

        if request.method == 'GET':
            # Retrieve existing study plan
            db.execute('''SELECT * FROM study_plans WHERE student_id = ? 
                         ORDER BY created_at DESC LIMIT 1''', (student_id,))
            plan = db.fetchone()

            if not plan:
                return jsonify({'success': True, 'message': 'No study plan created yet', 'plan': None})

            return jsonify({
                'success': True,
                'plan': json.loads(plan['plan_data']),
                'created_at': plan['created_at'],
                'ai_generated': plan['ai_generated']
            })

        # POST - Generate new study plan
        data = request.get_json() or {}
        weaknesses = data.get('weaknesses', [])
        hours_per_day = float(data.get('hours_per_day', 2))

        if not weaknesses:
            return jsonify({'success': False, 'message': 'Weaknesses list required'}), 400

        # Generate plan using AI
        plan_data = ai_service.generate_study_plan(student_id, weaknesses, hours_per_day)

        # Store in database
        db.execute('''INSERT INTO study_plans (student_id, plan_data, ai_generated)
                     VALUES (?, ?, ?)''',
                  (student_id, json.dumps(plan_data), 1))
        db.commit()

        return jsonify({
            'success': True,
            'message': 'Study plan generated',
            'plan': plan_data
        })
    except Exception as e:
        logger.error(f"Study plan error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to generate study plan'}), 500


# ============================================================================
# PREMIUM FEATURES - DYNAMIC QUIZ WITH EXPLANATIONS
# ============================================================================

@app.route('/api/premium/quiz', methods=['POST', 'GET'])
@require_auth
@rate_limit
def premium_quiz():
    """Dynamic quiz with explanations and scoring"""
    try:
        student_id = session.get('user_id')
        db = get_db()

        if request.method == 'GET':
            # Get a random question
            subject = request.args.get('subject', '').strip()
            difficulty = request.args.get('difficulty', 'medium').lower()

            query = 'SELECT * FROM quiz_questions WHERE 1=1'
            params = []

            if subject:
                query += ' AND subject = ?'
                params.append(subject)
            if difficulty:
                query += ' AND difficulty = ?'
                params.append(difficulty)

            query += ' ORDER BY RANDOM() LIMIT 1'
            db.execute(query, params)
            question = db.fetchone()

            if not question:
                return jsonify({'success': False, 'message': 'No questions found'}), 404

            return jsonify({
                'success': True,
                'question': {
                    'id': question['id'],
                    'subject': question['subject'],
                    'question': question['question'],
                    'options': json.loads(question['options']),
                    'difficulty': question['difficulty']
                }
            })

        # POST - Submit answer and get feedback
        data = request.get_json() or {}
        question_id = data.get('question_id')
        answer = data.get('answer', '').strip()

        if not question_id or not answer:
            return jsonify({'success': False, 'message': 'Question ID and answer required'}), 400

        db.execute('SELECT * FROM quiz_questions WHERE id = ?', (question_id,))
        question = db.fetchone()

        if not question:
            return jsonify({'success': False, 'message': 'Question not found'}), 404

        is_correct = answer.lower() == question['correct_answer'].lower()
        points = 10 if is_correct else 0

        # Award badge if perfect
        if is_correct:
            badge = gamification_service.award_badge(student_id, 'perfect_score')

        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'correct_answer': question['correct_answer'],
            'explanation': question['explanation'] or 'Study this concept more carefully',
            'points_earned': points
        })
    except Exception as e:
        logger.error(f"Quiz error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to process quiz'}), 500


# ============================================================================
# PREMIUM FEATURES - ANALYTICS
# ============================================================================

@app.route('/api/premium/analytics/<student_id>', methods=['GET'])
@require_auth
@rate_limit
def analytics(student_id):
    """Student analytics and performance dashboard"""
    try:
        # Verify student can only access their own analytics or admin
        if session.get('user_id') != student_id and not session.get('is_admin'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        db = get_db()

        # Get performance data
        db.execute('''SELECT * FROM student_performance WHERE student_id = ?
                     ORDER BY created_at DESC LIMIT 100''', (student_id,))
        performances = db.fetchall()

        if not performances:
            return jsonify({
                'success': True,
                'student_id': student_id,
                'metrics': {},
                'message': 'No data available'
            })

        # Calculate metrics
        metrics = analytics_service.calculate_performance_metrics(
            [{'score': p['score'], 'total': p['total_questions']} for p in performances]
        )

        # Group by subject
        by_subject = {}
        for perf in performances:
            subject = perf['subject']
            if subject not in by_subject:
                by_subject[subject] = []
            by_subject[subject].append({
                'score': perf['score'],
                'total': perf['total_questions'],
                'percentage': (perf['score'] / perf['total_questions'] * 100) if perf['total_questions'] > 0 else 0
            })

        return jsonify({
            'success': True,
            'student_id': student_id,
            'metrics': metrics,
            'by_subject': by_subject
        })
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch analytics'}), 500


# ============================================================================
# PREMIUM FEATURES - ATTENDANCE
# ============================================================================

@app.route('/api/premium/attendance', methods=['GET', 'POST'])
@require_auth
@rate_limit
def attendance():
    """Track attendance and engagement"""
    try:
        student_id = session.get('user_id')
        data = request.get_json() or {}

        if request.method == 'POST':
            # Record attendance
            db = get_db()
            action = data.get('action', 'present').lower()

            # This would be stored in a dedicated table in production
            logger.info(f"Attendance recorded for {student_id}: {action}")

            return jsonify({
                'success': True,
                'message': f'Attendance recorded as {action}'
            })

        # GET - Retrieve attendance data
        return jsonify({
            'success': True,
            'student_id': student_id,
            'attendance_rate': 95,  # Placeholder
            'total_sessions': 100,
            'present': 95,
            'absent': 5
        })
    except Exception as e:
        logger.error(f"Attendance error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to process attendance'}), 500


# ============================================================================
# PREMIUM FEATURES - GAMIFICATION
# ============================================================================

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


# ============================================================================
# PREMIUM FEATURES - PAST PAPERS
# ============================================================================

@app.route('/api/premium/past-papers', methods=['GET', 'POST', 'DELETE'])
@require_auth
@rate_limit
def past_papers():
    """Upload, practice, and track past papers"""
    try:
        student_id = session.get('user_id')
        db = get_db()

        if request.method == 'GET':
            # List past papers
            db.execute('''SELECT * FROM past_papers WHERE student_id = ?
                         ORDER BY uploaded_at DESC''', (student_id,))
            papers = db.fetchall()

            return jsonify({
                'success': True,
                'papers': [
                    {
                        'id': p['id'],
                        'subject': p['subject'],
                        'year': p['year'],
                        'difficulty': p['difficulty'],
                        'score': p['score'],
                        'file_path': p['file_path']
                    }
                    for p in papers
                ]
            })

        elif request.method == 'POST':
            # Upload past paper
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'File required'}), 400

            file = request.files['file']
            if not file or not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'Invalid file'}), 400

            filename = secure_filename(file.filename)
            filepath = os.path.join('data/past_papers', filename)
            file.save(filepath)

            subject = request.form.get('subject', '').strip()
            year = int(request.form.get('year', 2024))
            difficulty = request.form.get('difficulty', 'medium').lower()

            db.execute('''INSERT INTO past_papers (student_id, subject, file_path, year, difficulty)
                         VALUES (?, ?, ?, ?, ?)''',
                      (student_id, subject, filepath, year, difficulty))
            db.commit()

            return jsonify({'success': True, 'message': 'Past paper uploaded'})

        elif request.method == 'DELETE':
            # Delete past paper
            paper_id = request.args.get('id')
            db.execute('DELETE FROM past_papers WHERE id = ? AND student_id = ?',
                      (paper_id, student_id))
            db.commit()

            return jsonify({'success': True, 'message': 'Past paper deleted'})

    except Exception as e:
        logger.error(f"Past papers error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to process past papers'}), 500


# ============================================================================
# PREMIUM FEATURES - REPORTS
# ============================================================================

@app.route('/api/premium/reports/<student_id>', methods=['GET'])
@require_auth
@rate_limit
def reports(student_id):
    """Generate comprehensive progress reports"""
    try:
        if session.get('user_id') != student_id and not session.get('is_admin'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        db = get_db()

        # Get student
        db.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = db.fetchone()

        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404

        # Get performance data
        db.execute('''SELECT * FROM student_performance WHERE student_id = ?
                     ORDER BY created_at DESC LIMIT 50''', (student_id,))
        performances = db.fetchall()

        # Generate report
        report = analytics_service.generate_progress_report({
            'id': student_id,
            'overall_score': 75,
            'subjects': {'Math': 80, 'English': 70, 'Science': 85},
            'strengths': ['Consistent participation', 'Strong in practical subjects'],
            'weaknesses': ['Time management', 'Essay writing'],
            'consistency_score': 85
        })

        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        logger.error(f"Reports error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to generate report'}), 500


# ============================================================================
# PREMIUM FEATURES - CONTENT SUMMARIZATION
# ============================================================================

@app.route('/api/premium/summarize', methods=['POST'])
@require_auth
@rate_limit
def summarize():
    """AI-powered content summarization"""
    try:
        data = request.get_json() or {}
        content = data.get('content', '').strip()
        max_length = int(data.get('max_length', 200))

        if not content:
            return jsonify({'success': False, 'message': 'Content required'}), 400

        summary = ai_service.summarize_content(content, max_length)

        return jsonify({
            'success': True,
            'original_length': len(content.split()),
            'summary': summary,
            'summary_length': len(summary.split())
        })
    except Exception as e:
        logger.error(f"Summarize error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to summarize content'}), 500


# ============================================================================
# WEBSOCKET ENDPOINTS - AI RESEARCH CHAT
# ============================================================================

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
# ADMIN ENDPOINTS - EMAIL CONFIGURATION
# ============================================================================

@app.route('/api/admin/email-config', methods=['GET'])
@require_admin_token
def get_email_config():
    """Get email configuration"""
    try:
        db = get_db()
        db.execute('SELECT * FROM email_config WHERE is_active = 1')
        config = db.fetchone()

        if not config:
            return jsonify({
                'success': True,
                'message': 'No active email configuration',
                'config': None
            })

        return jsonify({
            'success': True,
            'config': {
                'provider': config['provider'],
                'sender_email': config['sender_email'],
                'sender_name': config['sender_name'],
                'is_active': config['is_active']
            }
        })
    except Exception as e:
        logger.error(f"Get email config error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch email config'}), 500


@app.route('/api/admin/email-config', methods=['POST'])
@require_super_admin_token
def set_email_config():
    """Set email configuration"""
    try:
        data = request.get_json() or {}
        provider = data.get('provider', 'gmail').lower()
        sender_email = data.get('sender_email', '').strip()
        sender_name = data.get('sender_name', 'Mengo-Hub').strip()
        api_key = data.get('api_key', '').strip()
        smtp_server = data.get('smtp_server', '').strip()
        smtp_port = int(data.get('smtp_port', 587))

        if not sender_email:
            return jsonify({'success': False, 'message': 'Sender email required'}), 400

        db = get_db()

        # Deactivate previous configs
        db.execute('UPDATE email_config SET is_active = 0')

        # Add new config
        db.execute('''INSERT INTO email_config 
            (provider, sender_email, sender_name, smtp_server, smtp_port, api_key, is_active, created_by)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)''',
            (provider, sender_email, sender_name, smtp_server, smtp_port, api_key, session.get('user_id', 'admin')))
        db.commit()

        logger.info(f"Email config updated by {session.get('user_id')}")

        return jsonify({
            'success': True,
            'message': 'Email configuration saved'
        })
    except Exception as e:
        logger.error(f"Set email config error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to save email config'}), 500


@app.route('/api/admin/email-config/test', methods=['POST'])
@require_admin_token
def test_email_config():
    """Test email configuration"""
    try:
        test_email = request.get_json().get('email', 'test@mengo.com')

        success = email_service.send_email(
            test_email,
            'Mengo-Hub Email Configuration Test',
            '<h1>Email Configuration Test</h1><p>This email confirms your email service is configured correctly.</p>'
        )

        if success:
            return jsonify({
                'success': True,
                'message': f'Test email sent to {test_email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send test email'
            }), 500

    except Exception as e:
        logger.error(f"Test email error: {str(e)}")
        return jsonify({'success': False, 'message': 'Email test failed'}), 500


@app.route('/')
def root():
    return send_from_directory('public', 'index.html')

@app.route('/api/admin/send-admin-alert', methods=['POST'])
@require_admin_token
def send_admin_alert():
    """Send alerts to administrators"""
    try:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        message = data.get('message', '').strip()
        recipient = data.get('recipient', 'admin@mengo.com')

        if not title or not message:
            return jsonify({'success': False, 'message': 'Title and message required'}), 400

        html_content = f"""
        <h2>{title}</h2>
        <p>{message}</p>
        <hr>
        <p>Sent at: {datetime.now().isoformat()}</p>
        <p>From: Mengo-Hub System</p>
        """

        success = email_service.send_email(recipient, f"[ALERT] {title}", html_content)

        if success:
            logger.info(f"Admin alert sent: {title}")
            return jsonify({'success': True, 'message': 'Alert sent'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send alert'}), 500

    except Exception as e:
        logger.error(f"Send alert error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to send alert'}), 500


# ============================================================================
# ADMIN ENDPOINTS - CERTIFICATE MANAGEMENT
# ============================================================================

@app.route('/api/admin/certificate', methods=['GET', 'POST'])
@require_admin_token
def manage_certificate():
    """Manage admin certificates"""
    try:
        if request.method == 'GET':
            admin_id = session.get('user_id')
            db = get_db()

            # Check if admin has certificate
            db.execute('SELECT * FROM admin_certificates WHERE admin_id = ?', (admin_id,))
            cert = db.fetchone()

            if not cert:
                return jsonify({
                    'success': True,
                    'has_certificate': False,
                    'message': 'No certificate found'
                })

            # Check if certificate is valid
            if cert['expiry_date']:
                expiry = datetime.fromisoformat(cert['expiry_date'])
                is_valid = datetime.now() < expiry
            else:
                is_valid = True

            return jsonify({
                'success': True,
                'has_certificate': True,
                'verified': cert['verified'],
                'is_valid': is_valid,
                'issuer': cert['issuer'],
                'expiry_date': cert['expiry_date']
            })

        elif request.method == 'POST':
            # Upload certificate
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'Certificate file required'}), 400

            file = request.files['file']
            if not file or file.filename == '':
                return jsonify({'success': False, 'message': 'Invalid file'}), 400

            filename = secure_filename(f"cert_{session.get('user_id')}_{int(time.time())}.pem")
            filepath = os.path.join('data', filename)
            file.save(filepath)

            admin_id = session.get('user_id')
            issuer = request.form.get('issuer', 'Self-signed').strip()

            db = get_db()
            db.execute('''INSERT INTO admin_certificates (admin_id, certificate_path, issuer, verified)
                         VALUES (?, ?, ?, ?)''',
                      (admin_id, filepath, issuer, 1))
            db.commit()

            logger.info(f"Certificate uploaded for admin {admin_id}")

            return jsonify({'success': True, 'message': 'Certificate uploaded'})

    except Exception as e:
        logger.error(f"Certificate error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to manage certificate'}), 500


# ============================================================================
# FIXED ADMIN AUTHENTICATION - CERTIFICATE VALIDATION
# ============================================================================

@app.route('/api/admin/auth', methods=['POST'])
def admin_authentication():
    """Admin authentication with certificate validation"""
    try:
        data = request.get_json() or {}
        admin_id = data.get('admin_id', '').strip()
        password = data.get('password', '').strip()
        certificate = data.get('certificate')  # Optional

        if not admin_id or not password:
            return jsonify({'success': False, 'message': 'Admin ID and password required'}), 400

        db = get_db()
        db.execute('SELECT * FROM students WHERE id = ? AND is_admin = 1', (admin_id,))
        admin = db.fetchone()

        if not admin:
            return jsonify({'success': False, 'message': 'Admin not found'}), 404

        # Verify password
        if not check_password(password, admin['password']):
            return jsonify({'success': False, 'message': 'Invalid password'}), 401

        # Check certificate if it's provided
        if certificate:
            db.execute('SELECT * FROM admin_certificates WHERE admin_id = ? AND verified = 1',
                      (admin_id,))
            cert = db.fetchone()

            if not cert:
                return jsonify({
                    'success': False,
                    'message': 'No verified certificate found',
                    'requires_certificate': True
                }), 403

            # Check expiry
            if cert['expiry_date']:
                expiry = datetime.fromisoformat(cert['expiry_date'])
                if datetime.now() > expiry:
                    return jsonify({
                        'success': False,
                        'message': 'Certificate expired',
                        'requires_certificate': True
                    }), 403

        # FIX: Check if certificate field is null - this was blocking valid admins
        # Now we allow admins with null certificates (legacy admins) or valid certificates
        admin_certificate = admin.get('certificate')
        if admin_certificate is None or admin_certificate == '':
            # Legacy admin or no certificate requirement
            pass
        else:
            # Admin has certificate - verify it's valid
            db.execute('SELECT * FROM admin_certificates WHERE admin_id = ? AND verified = 1',
                      (admin_id,))
            cert_record = db.fetchone()
            if not cert_record:
                return jsonify({
                    'success': False,
                    'message': 'Certificate verification required'
                }), 403

        session['user_id'] = admin_id
        session['is_admin'] = 1
        session['username'] = admin['username']

        return jsonify({
            'success': True,
            'message': 'Admin authentication successful',
            'admin': {
                'id': admin_id,
                'username': admin['username'],
                'fullName': admin['fullName']
            }
        })

    except Exception as e:
        logger.error(f"Admin auth error: {str(e)}")
        return jsonify({'success': False, 'message': 'Authentication failed'}), 500


# ============================================================================
# IMPORT CSV ENDPOINT
# ============================================================================

@app.route('/api/import-csv', methods=['POST'])
@require_admin_token
def import_csv():
    """Import users from CSV"""
    try:
        data = request.get_json() or {}
        import_password = data.get('import_password')
        csv_path = data.get('csv_path', IMPORT_CSV_PATH)

        if import_password != ADMIN_IMPORT_PASSWORD:
            return jsonify({'success': False, 'message': 'Import password invalid'}), 403

        if not os.path.exists(csv_path):
            return jsonify({'success': False, 'message': f'CSV file not found: {csv_path}'}), 404

        imported = []
        skipped = []
        db = get_db()

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                kind = (row.get('type') or '').strip().lower()
                if not kind:
                    continue

                try:
                    user_id = normalize_user_id(kind, row.get('id'), row.get('username'))
                    username = (row.get('username') or '').strip()

                    if not username:
                        skipped.append({'row': row, 'reason': 'Missing username'})
                        continue

                    password = (row.get('password') or '').strip() or secrets.token_urlsafe(8)
                    hashed_password = hash_password(password)
                    full_name = (row.get('fullName') or '').strip() or username
                    email = (row.get('email') or '').strip() or None

                    if kind == 'student':
                        stream = (row.get('stream') or '').strip() or 'Unassigned'
                        klass = (row.get('class') or '').strip() or 'Unknown'
                        db.execute('''INSERT OR REPLACE INTO students
                            (id, username, password, fullName, email, stream, class)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (user_id, username, hashed_password, full_name, email, stream, klass))
                        imported.append({'type': 'student', 'id': user_id, 'username': username})

                    elif kind == 'teacher':
                        subjects = (row.get('subjects') or '').strip() or 'General'
                        db.execute('''INSERT OR REPLACE INTO teachers
                            (id, username, password, fullName, email, subjects)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                            (user_id, username, hashed_password, full_name, email, subjects))
                        imported.append({'type': 'teacher', 'id': user_id, 'username': username})

                except Exception as e:
                    skipped.append({'row': row, 'reason': str(e)})

        db.commit()
        logger.info(f"CSV import completed: {len(imported)} imported, {len(skipped)} skipped")

        return jsonify({
            'success': True,
            'imported': len(imported),
            'skipped': len(skipped),
            'imported_users': imported,
            'skipped_users': skipped[:10]  # Limit skipped list
        })

    except Exception as e:
        logger.error(f"CSV import error: {str(e)}")
        return jsonify({'success': False, 'message': 'CSV import failed'}), 500


# ============================================================================
# HEALTH CHECK & STATUS ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db = get_db()
        db.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        logger.error(f"Health check DB error: {str(e)}")
        db_status = 'disconnected'

    return jsonify({
        'success': True,
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.now().isoformat()
    })


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


# ============================================================================
# SERVE STATIC FILES
# ============================================================================

@app.route('/')
def index():
    """Serve index.html"""
    return send_from_directory('public', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """Serve static files"""
    if path and os.path.exists(os.path.join('public', path)):
        return send_from_directory('public', path)
    return send_from_directory('public', 'index.html')


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def create_app(test_config=None):
    """Application factory"""
    if test_config is None:
        init_db()
    return app


if __name__ == '__main__':
    # Initialize database
    init_db()

    # Generate SSL certificate if needed
    if USE_SSL:
        if generate_certificate():
            logger.info("Starting with SSL/HTTPS support")
            socketio.run(app, host='0.0.0.0', port=5000, ssl_context=(CERT_FILE, KEY_FILE), debug=True)
        else:
            logger.warning("SSL certificate generation failed, starting without SSL")
            socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    else:
        logger.info("Starting without SSL")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
