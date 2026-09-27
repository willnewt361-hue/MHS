#!/usr/bin/env python3
"""
Mengo-Hub Database Population Script
Populates the database with sample data for testing and demonstration
"""

import sqlite3
import json
import bcrypt
from datetime import datetime

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def populate_database():
    conn = sqlite3.connect('data/mengo.db')
    cursor = conn.cursor()

    # Sample students (id, username, password, fullName, email, stream, class, role, photo, is_admin, certificate, payment_status, login_attempts, lockout_until, mental_wellbeing, decision_making, ambitions, hobbies, behavior_profile)
    students = [
        ('S001', 'john_doe', hash_password('password123'), 'John Doe', 'john@example.com', 'East', 'S1', 'Normal student', None, 0, None, 'paid', 0, None, 'Good', 'Confident', 'Doctor', 'Reading', 'Focused'),
        ('S002', 'jane_smith', hash_password('password123'), 'Jane Smith', 'jane@example.com', 'West', 'S2', 'Normal student', None, 0, None, 'paid', 0, None, 'Excellent', 'Decisive', 'Engineer', 'Sports', 'Motivated'),
        ('S003', 'bob_johnson', hash_password('password123'), 'Bob Johnson', 'bob@example.com', 'North', 'S3', 'Normal student', None, 0, None, 'unpaid', 0, None, 'Fair', 'Indecisive', 'Teacher', 'Music', 'Distracted'),
        ('A000', 'admin', hash_password('admin2026'), 'System Admin', 'admin@mengo.com', 'All', 'All', 'System Administrator', None, 1, None, 'paid', 0, None, None, None, None, None, None),
    ]

    # Sample teachers (id, username, password, fullName, email, subjects, stream, class, photo, quote, role, is_admin, certificate, payment_status, login_attempts, lockout_until)
    teachers = [
        ('T001', 'mr_math', hash_password('teacher123'), 'Mr. Mathematics', 'math@mengo.com', 'Mathematics', 'East', 'S1', None, 'Mathematics is the language of the universe', 'Normal teacher', 0, None, 'paid', 0, None),
        ('T002', 'ms_english', hash_password('teacher123'), 'Ms. English', 'english@mengo.com', 'English', 'West', 'S2', None, 'Literature opens minds and hearts', 'Normal teacher', 0, None, 'paid', 0, None),
        ('T003', 'dr_science', hash_password('teacher123'), 'Dr. Science', 'science@mengo.com', 'Physics,Chemistry,Biology', 'North', 'S3', None, 'Science explains the wonders of nature', 'Normal teacher', 0, None, 'paid', 0, None),
    ]

    # Insert students
    cursor.executemany('''
        INSERT OR REPLACE INTO students
        (id, username, password, fullName, email, stream, class, role, photo, is_admin, certificate, payment_status, login_attempts, lockout_until, mental_wellbeing, decision_making, ambitions, hobbies, behavior_profile)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', students)

    # Insert teachers
    cursor.executemany('''
        INSERT OR REPLACE INTO teachers
        (id, username, password, fullName, email, subjects, stream, class, photo, quote, role, is_admin, certificate, payment_status, login_attempts, lockout_until)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', teachers)

    # Sample quiz questions
    quiz_questions = [
        ('Mathematics', 'What is the value of π (pi) to 2 decimal places?', '["3.14", "3.15", "3.16", "3.17"]', '3.14', 'π is approximately 3.14159, so to 2 decimal places it is 3.14', 'easy'),
        ('Mathematics', 'Solve for x: 2x + 3 = 7', '["x = 2", "x = 3", "x = 4", "x = 5"]', 'x = 2', 'Subtract 3 from both sides: 2x = 4, then divide by 2: x = 2', 'easy'),
        ('English', 'What is the synonym of "happy"?', '["Sad", "Joyful", "Angry", "Tired"]', 'Joyful', 'Happy and joyful both mean feeling pleasure or contentment', 'easy'),
        ('Physics', 'What is the SI unit of force?', '["Newton", "Joule", "Watt", "Pascal"]', 'Newton', 'The Newton (N) is the SI unit of force, named after Sir Isaac Newton', 'medium'),
        ('Chemistry', 'What is the chemical symbol for gold?', '["Go", "Gd", "Au", "Ag"]', 'Au', 'Au comes from the Latin word "aurum" meaning gold', 'easy'),
    ]

    cursor.executemany('''
        INSERT OR REPLACE INTO quiz_questions
        (subject, question, options, correct_answer, explanation, difficulty)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', quiz_questions)

    # Sample student performance data
    performance_data = [
        ('S001', 'Mathematics', 85.0, 10, '["algebra", "geometry"]', '["Practice more algebraic equations", "Review geometry theorems"]'),
        ('S001', 'English', 92.0, 10, '["grammar"]', '["Continue practicing grammar rules"]'),
        ('S002', 'Mathematics', 78.0, 10, '["calculus", "trigonometry"]', '["Focus on trigonometric identities", "Practice calculus problems"]'),
        ('S002', 'Physics', 88.0, 10, '["mechanics"]', '["Review Newton\'s laws of motion"]'),
    ]

    cursor.executemany('''
        INSERT OR REPLACE INTO student_performance
        (student_id, subject, score, total_questions, weaknesses, recommendations)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', performance_data)

    # Sample study plans
    study_plans = [
        ('S001', json.dumps({
            'daily_schedule': [
                {'time': '8:00 AM', 'activity': 'Mathematics revision - focus on algebra'},
                {'time': '10:00 AM', 'activity': 'English grammar practice'},
                {'time': '2:00 PM', 'activity': 'Physics problem solving'},
                {'time': '4:00 PM', 'activity': 'Review weak areas and take quiz'}
            ],
            'weekly_goals': ['Complete 5 math exercises', 'Read 2 English passages', 'Practice 3 physics topics'],
            'weakness_focus': ['Algebra', 'Geometry'],
            'ai_generated': True
        }), 1),
        ('S002', json.dumps({
            'daily_schedule': [
                {'time': '9:00 AM', 'activity': 'Chemistry lab work'},
                {'time': '11:00 AM', 'activity': 'Biology study'},
                {'time': '3:00 PM', 'activity': 'Mathematics practice'},
                {'time': '5:00 PM', 'activity': 'Review and assessment'}
            ],
            'weekly_goals': ['Complete 3 chemistry experiments', 'Study 4 biology topics', 'Solve 10 math problems'],
            'weakness_focus': ['Organic chemistry', 'Calculus'],
            'ai_generated': True
        }), 1),
    ]

    cursor.executemany('''
        INSERT OR REPLACE INTO study_plans
        (student_id, plan_data, ai_generated)
        VALUES (?, ?, ?)
    ''', study_plans)

    # Sample messages
    messages = [
        ('S001', 'T001', 'student', 'S001', 'Hello Mr. Mathematics, I need help with algebra equations.', None, 1),
        ('S001', 'T001', 'teacher', 'T001', 'Hi John! I\'d be happy to help. Which specific algebra topic are you struggling with?', None, 1),
        ('S002', 'T002', 'student', 'S002', 'Ms. English, can you check my essay?', None, 1),
        ('S002', 'T002', 'teacher', 'T002', 'Of course Jane! Please share your essay and I\'ll provide detailed feedback.', None, 1),
    ]

    cursor.executemany('''
        INSERT OR REPLACE INTO messages
        (student_id, teacher_id, from_role, sender_id, message, attachment_name, is_read)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', messages)

    conn.commit()
    conn.close()
    print("Database populated with sample data successfully!")

if __name__ == '__main__':
    populate_database()