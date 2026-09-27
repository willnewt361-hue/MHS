-- Mengo-Hub Database Schema (PostgreSQL)
-- This is the production database schema for PostgreSQL
-- Created: 2026-05-05

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    fullName VARCHAR(150) NOT NULL,
    email VARCHAR(100),
    stream VARCHAR(50),
    class VARCHAR(50),
    role VARCHAR(100),
    photo VARCHAR(255),
    is_admin INTEGER DEFAULT 0,
    certificate VARCHAR(255),
    payment_status VARCHAR(50) DEFAULT 'unpaid',
    login_attempts INTEGER DEFAULT 0,
    lockout_until TIMESTAMP,
    mental_wellbeing VARCHAR(100),
    decision_making VARCHAR(100),
    ambitions VARCHAR(100),
    hobbies VARCHAR(100),
    behavior_profile VARCHAR(100),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teachers Table
CREATE TABLE IF NOT EXISTS teachers (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    fullName VARCHAR(150) NOT NULL,
    email VARCHAR(100),
    subjects VARCHAR(255),
    stream VARCHAR(50),
    class VARCHAR(50),
    photo VARCHAR(255),
    quote TEXT,
    role VARCHAR(100),
    is_admin INTEGER DEFAULT 0,
    certificate VARCHAR(255),
    payment_status VARCHAR(50) DEFAULT 'unpaid',
    login_attempts INTEGER DEFAULT 0,
    lockout_until TIMESTAMP,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Login Logs Table
CREATE TABLE IF NOT EXISTS loginLogs (
    id SERIAL PRIMARY KEY,
    userId VARCHAR(50) NOT NULL,
    userType VARCHAR(50) NOT NULL,
    username VARCHAR(100) NOT NULL,
    ipAddress VARCHAR(45),
    action VARCHAR(100),
    loginTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    teacher_id VARCHAR(50) NOT NULL,
    from_role VARCHAR(50) NOT NULL,
    sender_id VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    attachment_name VARCHAR(255),
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);

-- Quiz Questions Table
CREATE TABLE IF NOT EXISTS quiz_questions (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    options JSON,
    correct_answer VARCHAR(255),
    explanation TEXT,
    difficulty VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student Performance Table
CREATE TABLE IF NOT EXISTS student_performance (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    subject VARCHAR(100),
    score DECIMAL(5, 2),
    weaknesses JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Study Plans Table
CREATE TABLE IF NOT EXISTS study_plans (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    plan_data JSON,
    ai_generated INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2),
    status VARCHAR(50),
    transaction_id VARCHAR(255),
    payment_method VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Assignments Table
CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    teacher_id VARCHAR(50) NOT NULL,
    teacher_name VARCHAR(150) NOT NULL,
    stream VARCHAR(50),
    class VARCHAR(50),
    subject VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Updates Table
CREATE TABLE IF NOT EXISTS updates (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    fullName VARCHAR(150) NOT NULL,
    role VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    user_type VARCHAR(50),
    feedback_text TEXT,
    rating INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Premium Features Tables

-- Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'present',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(student_id, date)
);

-- Gamification Points
CREATE TABLE IF NOT EXISTS student_points (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    action VARCHAR(100),
    points INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Badges
CREATE TABLE IF NOT EXISTS student_badges (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    badge_key VARCHAR(100),
    badge_name VARCHAR(255),
    awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(student_id, badge_key)
);

-- Past Papers
CREATE TABLE IF NOT EXISTS past_papers (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    year INTEGER,
    exam_type VARCHAR(100),
    file_path VARCHAR(255),
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Past Paper Attempts
CREATE TABLE IF NOT EXISTS past_paper_attempts (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    paper_id INTEGER NOT NULL,
    score DECIMAL(5, 2),
    total_score DECIMAL(5, 2),
    duration_minutes INTEGER,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES past_papers(id) ON DELETE CASCADE
);

-- Research Sessions (WebSocket AI)
CREATE TABLE IF NOT EXISTS research_sessions (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    subject VARCHAR(100),
    topic VARCHAR(255),
    session_data JSON,
    duration_minutes INTEGER,
    ai_provider VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- AI Chat Messages
CREATE TABLE IF NOT EXISTS ai_chat_messages (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    message_text TEXT,
    ai_response TEXT,
    ai_provider VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Admin Email Configuration
CREATE TABLE IF NOT EXISTS email_configuration (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(50),
    email_provider VARCHAR(50),
    smtp_server VARCHAR(255),
    smtp_port INTEGER,
    sender_email VARCHAR(255),
    is_configured INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(admin_id, email_provider)
);

-- System Settings
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_students_username ON students(username);
CREATE INDEX IF NOT EXISTS idx_students_is_admin ON students(is_admin);
CREATE INDEX IF NOT EXISTS idx_teachers_username ON teachers(username);
CREATE INDEX IF NOT EXISTS idx_messages_student_teacher ON messages(student_id, teacher_id);
CREATE INDEX IF NOT EXISTS idx_student_performance_student ON student_performance(student_id);
CREATE INDEX IF NOT EXISTS idx_login_logs_user ON loginLogs(userId, userType);
CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX IF NOT EXISTS idx_student_badges_student ON student_badges(student_id);
CREATE INDEX IF NOT EXISTS idx_past_paper_attempts_student ON past_paper_attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_research_sessions_student ON research_sessions(student_id);

-- Insert Default Admin User
INSERT INTO students (id, username, password, fullName, email, stream, class, role, is_admin, payment_status, createdAt)
VALUES (
    'A000',
    'admin',
    '$2b$12$KIXxPfxr1d5N0Z9QbqVzc.QbOE0H3Z9GQVP9qV3K7Q2E5R3W9YuKy', -- bcrypt hash of 'admin2026'
    'System Admin',
    'admin@mengo.com',
    'All',
    'All',
    'System Administrator',
    1,
    'paid',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

-- Insert Sample Teachers
INSERT INTO teachers (id, username, password, fullName, email, subjects, stream, class, role, is_admin, payment_status, createdAt)
VALUES
    ('T001', 'mr_math', '$2b$12$KIXxPfxr1d5N0Z9QbqVzc.QbOE0H3Z9GQVP9qV3K7Q2E5R3W9YuKy', 'Mr. Mathematics', 'math@mengo.com', 'Mathematics', 'East', 'S1', 'Normal teacher', 0, 'paid', CURRENT_TIMESTAMP),
    ('T002', 'ms_english', '$2b$12$KIXxPfxr1d5N0Z9QbqVzc.QbOE0H3Z9GQVP9qV3K7Q2E5R3W9YuKy', 'Ms. English', 'english@mengo.com', 'English', 'West', 'S2', 'Normal teacher', 0, 'paid', CURRENT_TIMESTAMP),
    ('T003', 'dr_science', '$2b$12$KIXxPfxr1d5N0Z9QbqVzc.QbOE0H3Z9GQVP9qV3K7Q2E5R3W9YuKy', 'Dr. Science', 'science@mengo.com', 'Physics,Chemistry,Biology', 'North', 'S3', 'Normal teacher', 0, 'paid', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Insert Sample Students
INSERT INTO students (id, username, password, fullName, email, stream, class, role, is_admin, payment_status, mental_wellbeing, decision_making, ambitions, hobbies, behavior_profile, createdAt)
VALUES
    ('S001', 'john_doe', '$2b$12$KIXxPfxr1d5N0Z9QbqVzc.QbOE0H3Z9GQVP9qV3K7Q2E5R3W9YuKy', 'John Doe', 'john@example.com', 'East', 'S1', 'Normal student', 0, 'paid', 'Good', 'Confident', 'Doctor', 'Reading', 'Focused', CURRENT_TIMESTAMP),
    ('S002', 'jane_smith', '$2b$12$KIXxPfxr1d5N0Z9QbqVzc.QbOE0H3Z9GQVP9qV3K7Q2E5R3W9YuKy', 'Jane Smith', 'jane@example.com', 'West', 'S2', 'Normal student', 0, 'paid', 'Excellent', 'Decisive', 'Engineer', 'Sports', 'Motivated', CURRENT_TIMESTAMP),
    ('S003', 'bob_johnson', '$2b$12$KIXxPfxr1d5N0Z9QbqVzc.QbOE0H3Z9GQVP9qV3K7Q2E5R3W9YuKy', 'Bob Johnson', 'bob@example.com', 'North', 'S3', 'Normal student', 0, 'unpaid', 'Fair', 'Indecisive', 'Teacher', 'Music', 'Distracted', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- AUDIO & MEDIA SYSTEM TABLES
-- ============================================================================

-- Audio Files Table
CREATE TABLE IF NOT EXISTS audio_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    duration_seconds INTEGER,
    audio_type VARCHAR(50), -- 'beat', 'music_overlay', 'nature_sound', 'voice'
    category VARCHAR(100),
    uploaded_by VARCHAR(50),
    is_public INTEGER DEFAULT 1,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES students(id) ON DELETE SET NULL
);

-- Playlists Table
CREATE TABLE IF NOT EXISTS playlists (
    id SERIAL PRIMARY KEY,
    playlist_name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by VARCHAR(50) NOT NULL,
    is_public INTEGER DEFAULT 1,
    cover_image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES students(id) ON DELETE CASCADE
);

-- Playlist Items
CREATE TABLE IF NOT EXISTS playlist_items (
    id SERIAL PRIMARY KEY,
    playlist_id INTEGER NOT NULL,
    audio_id INTEGER NOT NULL,
    position INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (audio_id) REFERENCES audio_files(id) ON DELETE CASCADE,
    UNIQUE(playlist_id, audio_id)
);

-- Music Overlays (Curated collections)
CREATE TABLE IF NOT EXISTS music_overlays (
    id SERIAL PRIMARY KEY,
    overlay_name VARCHAR(255) NOT NULL,
    description TEXT,
    base_frequency INTEGER, -- Hz for binaural beats
    environment_type VARCHAR(100), -- 'nature', 'ambient', 'focused_study'
    audio_id INTEGER NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audio_id) REFERENCES audio_files(id) ON DELETE CASCADE
);

-- Audio Playback History
CREATE TABLE IF NOT EXISTS audio_playback_history (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    audio_id INTEGER NOT NULL,
    play_duration_seconds INTEGER,
    completed INTEGER DEFAULT 0,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (audio_id) REFERENCES audio_files(id) ON DELETE CASCADE
);

-- ============================================================================
-- DOCUMENT MANAGEMENT SYSTEM TABLES
-- ============================================================================

-- Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50), -- 'pdf', 'docx', 'txt'
    document_type VARCHAR(100), -- 'class_notes', 'teacher_notes', 'procedure', 'reference'
    subject VARCHAR(100),
    academic_level VARCHAR(50), -- 'S1', 'S2', 'S3', 'S4', 'S5', 'S6'
    uploaded_by VARCHAR(50),
    title VARCHAR(255),
    description TEXT,
    version INTEGER DEFAULT 1,
    is_public INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Document Categories
CREATE TABLE IF NOT EXISTS document_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document Access Control
CREATE TABLE IF NOT EXISTS document_access (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    access_level VARCHAR(50), -- 'view', 'download', 'print'
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(document_id, student_id)
);

-- Document Download Tracking
CREATE TABLE IF NOT EXISTS document_downloads (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Document Versions
CREATE TABLE IF NOT EXISTS document_versions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    version INTEGER,
    file_path VARCHAR(500),
    uploaded_by VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES teachers(id) ON DELETE SET NULL
);

-- ============================================================================
-- ASSESSMENT & EXAM SYSTEM TABLES
-- ============================================================================

-- Exams/Tests Table
CREATE TABLE IF NOT EXISTS exams (
    id SERIAL PRIMARY KEY,
    exam_name VARCHAR(255) NOT NULL,
    subject VARCHAR(100),
    academic_level VARCHAR(50),
    created_by VARCHAR(50),
    total_questions INTEGER,
    total_marks DECIMAL(8, 2),
    duration_minutes INTEGER,
    exam_type VARCHAR(100), -- 'midterm', 'final', 'quiz', 'mock'
    passing_score DECIMAL(8, 2),
    instructions TEXT,
    is_published INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Questions Table
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50), -- 'multiple_choice', 'short_answer', 'essay', 'true_false'
    options JSON, -- For multiple choice
    correct_answer TEXT,
    marks DECIMAL(8, 2),
    question_order INTEGER,
    explanation TEXT,
    difficulty_level VARCHAR(50), -- 'easy', 'medium', 'hard'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);

-- Question Bank (Reusable questions)
CREATE TABLE IF NOT EXISTS question_bank (
    id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    subject VARCHAR(100),
    question_type VARCHAR(50),
    options JSON,
    correct_answer TEXT,
    marks DECIMAL(8, 2),
    difficulty_level VARCHAR(50),
    created_by VARCHAR(50),
    is_public INTEGER DEFAULT 0,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Student Exam Submissions
CREATE TABLE IF NOT EXISTS exam_submissions (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    submitted_at TIMESTAMP,
    total_score DECIMAL(8, 2),
    max_score DECIMAL(8, 2),
    percentage DECIMAL(5, 2),
    status VARCHAR(50), -- 'in_progress', 'submitted', 'graded'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Student Exam Answers
CREATE TABLE IF NOT EXISTS exam_answers (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    student_answer TEXT,
    marks_awarded DECIMAL(8, 2),
    is_correct INTEGER DEFAULT 0,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES exam_submissions(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Marking Rubrics
CREATE TABLE IF NOT EXISTS marking_rubrics (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER,
    rubric_name VARCHAR(255),
    criteria JSON, -- Array of criteria with max points
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Teacher Marking Records
CREATE TABLE IF NOT EXISTS teacher_marking_records (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL,
    teacher_id VARCHAR(50) NOT NULL,
    feedback TEXT,
    marks_awarded DECIMAL(8, 2),
    marking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    style_indicator JSON, -- Track marking patterns
    FOREIGN KEY (submission_id) REFERENCES exam_submissions(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);

-- ============================================================================
-- COMMUNICATION & CHAT SYSTEM TABLES
-- ============================================================================

-- Chat Groups
CREATE TABLE IF NOT EXISTS chat_groups (
    id SERIAL PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by VARCHAR(50),
    group_type VARCHAR(50), -- 'class', 'project', 'general'
    avatar_url VARCHAR(255),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES students(id) ON DELETE SET NULL
);

-- Chat Group Members
CREATE TABLE IF NOT EXISTS chat_group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(50), -- 'admin', 'member'
    FOREIGN KEY (group_id) REFERENCES chat_groups(id) ON DELETE CASCADE,
    UNIQUE(group_id, user_id)
);

-- Chat Messages (Group & Direct)
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    group_id INTEGER, -- NULL for direct messages
    sender_id VARCHAR(50) NOT NULL,
    recipient_id VARCHAR(50), -- NULL for group, populated for DMs
    message_text TEXT,
    message_type VARCHAR(50), -- 'text', 'file', 'image', 'audio'
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    is_read INTEGER DEFAULT 0,
    read_at TIMESTAMP,
    edited_at TIMESTAMP,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES chat_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Chat Message Reactions
CREATE TABLE IF NOT EXISTS chat_reactions (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    emoji VARCHAR(10),
    reacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES chat_messages(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(message_id, user_id, emoji)
);

-- Feature Toggle Settings (Chat, etc.)
CREATE TABLE IF NOT EXISTS feature_toggles (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) UNIQUE NOT NULL,
    is_enabled INTEGER DEFAULT 1,
    is_global INTEGER DEFAULT 1, -- If 0, can be per-user
    disabled_message VARCHAR(255),
    disabled_until TIMESTAMP, -- NULL for permanent disable
    updated_by VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PAYMENT & SUBSCRIPTION SYSTEM TABLES
-- ============================================================================

-- Subscription Plans
CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(100) UNIQUE NOT NULL,
    plan_type VARCHAR(50), -- 'basic', 'premium'
    price DECIMAL(10, 2),
    currency VARCHAR(10), -- 'USD', 'UGX'
    billing_cycle VARCHAR(50), -- 'monthly', 'yearly'
    description TEXT,
    features JSON, -- Array of features included
    max_users INTEGER, -- -1 for unlimited
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Subscriptions
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    plan_id INTEGER NOT NULL,
    subscription_status VARCHAR(50), -- 'active', 'paused', 'cancelled', 'expired'
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    auto_renew INTEGER DEFAULT 1,
    auto_renew_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id) ON DELETE RESTRICT
);

-- Payment Transactions
CREATE TABLE IF NOT EXISTS payment_transactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    subscription_id INTEGER,
    amount DECIMAL(10, 2),
    currency VARCHAR(10),
    payment_method VARCHAR(50), -- 'mtn', 'airtel', 'stripe', 'credit_card'
    transaction_id VARCHAR(255) UNIQUE,
    external_reference VARCHAR(255), -- Payment processor reference
    status VARCHAR(50), -- 'pending', 'completed', 'failed', 'refunded'
    payment_gateway_response JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES user_subscriptions(id) ON DELETE SET NULL
);

-- MTN Mobile Money Integration
CREATE TABLE IF NOT EXISTS mtn_payments (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(50),
    phone_number VARCHAR(20),
    amount DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'UGX',
    status VARCHAR(50), -- 'pending', 'completed', 'failed'
    mtn_request_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE SET NULL
);

-- Airtel Money Integration
CREATE TABLE IF NOT EXISTS airtel_payments (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(50),
    phone_number VARCHAR(20),
    amount DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'UGX',
    status VARCHAR(50), -- 'pending', 'completed', 'failed'
    airtel_request_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE SET NULL
);

-- Invoices
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    transaction_id INTEGER,
    amount DECIMAL(10, 2),
    currency VARCHAR(10),
    invoice_date DATE,
    due_date DATE,
    status VARCHAR(50), -- 'draft', 'sent', 'paid', 'overdue'
    pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES payment_transactions(id) ON DELETE SET NULL
);

-- ============================================================================
-- BADGES, CERTIFICATES & GAMIFICATION TABLES
-- ============================================================================

-- Badge Templates
CREATE TABLE IF NOT EXISTS badge_templates (
    id SERIAL PRIMARY KEY,
    badge_name VARCHAR(100) UNIQUE NOT NULL,
    badge_code VARCHAR(50),
    description TEXT,
    icon_path VARCHAR(255),
    emoji_code VARCHAR(20),
    color_hex VARCHAR(10),
    points_value INTEGER,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Achievement Criteria
CREATE TABLE IF NOT EXISTS achievement_criteria (
    id SERIAL PRIMARY KEY,
    badge_id INTEGER NOT NULL,
    criteria_name VARCHAR(100),
    criteria_type VARCHAR(50), -- 'score_threshold', 'completion_count', 'streak', 'submission'
    criteria_value VARCHAR(255),
    threshold_value DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (badge_id) REFERENCES badge_templates(id) ON DELETE CASCADE
);

-- Student Badges (Awarded)
CREATE TABLE IF NOT EXISTS student_badges_awarded (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    badge_id INTEGER NOT NULL,
    awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    earned_by_criteria_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badge_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (earned_by_criteria_id) REFERENCES achievement_criteria(id) ON DELETE SET NULL,
    UNIQUE(student_id, badge_id)
);

-- Certificate Templates
CREATE TABLE IF NOT EXISTS certificate_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,
    template_path VARCHAR(255), -- Path to template file
    variables JSON, -- Placeholders like {{student_name}}, {{date}}
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Certificates Issued
CREATE TABLE IF NOT EXISTS certificates_issued (
    id SERIAL PRIMARY KEY,
    certificate_id VARCHAR(100) UNIQUE NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    template_id INTEGER NOT NULL,
    achievement_type VARCHAR(100), -- 'course_completion', 'exam_pass', 'badge'
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    issued_by VARCHAR(50),
    pdf_path VARCHAR(255),
    verification_code VARCHAR(50),
    is_revoked INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES certificate_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (issued_by) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Student Portfolio
CREATE TABLE IF NOT EXISTS student_portfolio (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    portfolio_data JSON, -- Badges, certificates, achievements
    total_points INTEGER DEFAULT 0,
    total_achievements INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(student_id)
);

-- ============================================================================
-- ADMIN & SECURITY TABLES
-- ============================================================================

-- Admin Announcements
CREATE TABLE IF NOT EXISTS admin_announcements (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(50) NOT NULL,
    admin_name VARCHAR(150),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    target_users VARCHAR(50) DEFAULT 'all',  -- 'all', 'students', 'teachers', 'admins'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    views_count INTEGER DEFAULT 0,
    FOREIGN KEY (admin_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Super Admin Certificates
CREATE TABLE IF NOT EXISTS super_admin_certificates (
    id SERIAL PRIMARY KEY,
    certificate_id VARCHAR(100) UNIQUE NOT NULL,
    admin_id VARCHAR(50) NOT NULL,
    certificate_code VARCHAR(255),
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    is_revoked INTEGER DEFAULT 0,
    revoked_at TIMESTAMP,
    issued_by VARCHAR(50),
    FOREIGN KEY (admin_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (issued_by) REFERENCES students(id) ON DELETE SET NULL,
    UNIQUE(admin_id)
);

-- Admin API Tokens
CREATE TABLE IF NOT EXISTS admin_api_tokens (
    id SERIAL PRIMARY KEY,
    token_id VARCHAR(100) UNIQUE NOT NULL,
    admin_id VARCHAR(50) NOT NULL,
    token_hash VARCHAR(255),
    token_name VARCHAR(100),
    is_active INTEGER DEFAULT 1,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Password History
CREATE TABLE IF NOT EXISTS password_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255),
    set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(100), -- 'login', 'logout', 'create', 'update', 'delete', 'admin_action'
    user_id VARCHAR(50),
    admin_id VARCHAR(50),
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(50), -- 'success', 'failed'
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_date ON audit_logs(created_at);

-- System Settings & Configuration
CREATE TABLE IF NOT EXISTS system_configuration (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(50), -- 'string', 'number', 'boolean', 'json'
    description TEXT,
    updated_by VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES students(id) ON DELETE SET NULL
);

-- ============================================================================
-- VIDEO & MEDIA TABLES
-- ============================================================================

-- Videos
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    file_size INTEGER,
    duration_seconds INTEGER,
    thumbnail_path VARCHAR(255),
    subject VARCHAR(100),
    academic_level VARCHAR(50),
    uploaded_by VARCHAR(50),
    video_quality VARCHAR(50), -- '360p', '480p', '720p', '1080p'
    is_public INTEGER DEFAULT 1,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Video Views
CREATE TABLE IF NOT EXISTS video_views (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    watch_duration_seconds INTEGER,
    watched_percentage DECIMAL(5, 2),
    completed INTEGER DEFAULT 0,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Video Transcripts
CREATE TABLE IF NOT EXISTS video_transcripts (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL,
    transcript_text TEXT,
    language VARCHAR(20) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
);

-- ============================================================================
-- TEXT SCANNER & OCR TABLES
-- ============================================================================

-- Scanned Documents
CREATE TABLE IF NOT EXISTS scanned_documents (
    id SERIAL PRIMARY KEY,
    original_file_path VARCHAR(500),
    scanned_text_path VARCHAR(500),
    student_id VARCHAR(50),
    scanner_type VARCHAR(50), -- 'basic', 'premium'
    confidence_score DECIMAL(5, 2),
    languages_detected JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
);

-- ============================================================================
-- OFFLINE SYNC TABLES
-- ============================================================================

-- Offline Sync Queue
CREATE TABLE IF NOT EXISTS offline_sync_queue (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    sync_type VARCHAR(50), -- 'documents', 'videos', 'audio', 'messages'
    resource_id INTEGER,
    status VARCHAR(50), -- 'pending', 'synced', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ============================================================================
-- ANALYTICS & REPORTING TABLES
-- ============================================================================
-- Student Performance Analytics
CREATE TABLE IF NOT EXISTS student_analytics (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    analytics_period VARCHAR(50), -- 'daily', 'weekly', 'monthly'
    period_date DATE,
    average_score DECIMAL(5, 2),
    total_submissions INTEGER,
    average_completion_time INTEGER,
    engagement_score DECIMAL(5, 2),
    learning_velocity DECIMAL(5, 2),
    strengths JSON,
    weaknesses JSON,
    recommendations TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- System Health Metrics
CREATE TABLE IF NOT EXISTS system_health_metrics (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(100), -- 'storage_usage', 'concurrent_users', 'response_time'
    metric_value DECIMAL(15, 2),
    unit VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSON
);

-- ============================================================================
-- N8N WORKFLOWS TABLES
-- ============================================================================
-- Workflow Triggers
CREATE TABLE IF NOT EXISTS workflow_triggers (
    id SERIAL PRIMARY KEY,
    workflow_name VARCHAR(255) NOT NULL,
    trigger_type VARCHAR(50), -- 'scheduled', 'webhook', 'event'
    trigger_schedule VARCHAR(255), -- Cron expression or frequency
    last_execution TIMESTAMP,
    next_execution TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow Execution Logs
CREATE TABLE IF NOT EXISTS workflow_execution_logs (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL,
    execution_start TIMESTAMP,
    execution_end TIMESTAMP,
    status VARCHAR(50), -- 'success', 'failed', 'partial'
    error_message TEXT,
    execution_details JSON,
    FOREIGN KEY (workflow_id) REFERENCES workflow_triggers(id) ON DELETE CASCADE
);

-- ============================================================================
-- 3D VISUALIZATION TABLES
-- ============================================================================
-- 3D Models/Diagrams
CREATE TABLE IF NOT EXISTS three_d_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100),
    model_file_path VARCHAR(500),
    thumbnail_path VARCHAR(255),
    model_format VARCHAR(50), -- 'gltf', 'obj', 'fbx'
    created_by VARCHAR(50),
    is_interactive INTEGER DEFAULT 1,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES teachers(id) ON DELETE SET NULL
);

-- 3D Model Views
CREATE TABLE IF NOT EXISTS three_d_model_views (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    interaction_data JSON, -- Rotation, zoom, annotations
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES three_d_models(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ============================================================================
-- STORAGE MONITORING TABLES
-- ============================================================================
-- Storage Usage Tracking
CREATE TABLE IF NOT EXISTS storage_usage (
    id SERIAL PRIMARY KEY,
    resource_type VARCHAR(50), -- 'audio', 'video', 'documents', 'database'
    total_size_bytes BIGINT,
    file_count INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_audio_files_type ON audio_files(audio_type);
CREATE INDEX IF NOT EXISTS idx_audio_files_category ON audio_files(category);
CREATE INDEX IF NOT EXISTS idx_playlists_creator ON playlists(created_by);
CREATE INDEX IF NOT EXISTS idx_documents_subject ON documents(subject);
CREATE INDEX IF NOT EXISTS idx_documents_level ON documents(academic_level);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_exams_subject ON exams(subject);
CREATE INDEX IF NOT EXISTS idx_exams_level ON exams(academic_level);
CREATE INDEX IF NOT EXISTS idx_exam_submissions_student ON exam_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_exam_submissions_exam ON exam_submissions(exam_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_group ON chat_messages(group_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_sender ON chat_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_time ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_user ON payment_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON user_subscriptions(subscription_status);
CREATE INDEX IF NOT EXISTS idx_student_badges_awarded_student ON student_badges_awarded(student_id);
CREATE INDEX IF NOT EXISTS idx_certificates_student ON certificates_issued(student_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_date ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_videos_subject ON videos(subject);
CREATE INDEX IF NOT EXISTS idx_videos_level ON videos(academic_level);
CREATE INDEX IF NOT EXISTS idx_student_analytics_date ON student_analytics(period_date);
CREATE INDEX IF NOT EXISTS idx_storage_usage_time ON storage_usage(recorded_at);
