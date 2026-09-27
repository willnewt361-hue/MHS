# PostgreSQL Setup Guide for Mengo-Hub

## Overview
The `schema.sql` file contains the complete PostgreSQL database schema for production deployment. This replaces the SQLite `mengo.db` file used in development.

## Installation

### 1. Install PostgreSQL
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **Mac**: Use Homebrew: `brew install postgresql`
- **Linux**: Use package manager: `sudo apt install postgresql postgresql-contrib`

### 2. Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE mengo_hub;

# Connect to database
\c mengo_hub

# Load schema
\i /path/to/schema.sql

# Exit
\q
```

### 3. Update Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create or update `.env` file:

```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/mengo_hub
ADMIN_SECRET_KEY=Newton
ADMIN_SECRET_PASSWORD=##0000
```

### 5. Update Flask Application (Future)
The application will be updated to support both SQLite and PostgreSQL based on the `DATABASE_TYPE` environment variable.

## Database Tables
### Core Tables:
- **students** - Student user accounts and profiles
- **teachers** - Teacher user accounts and profiles
- **loginLogs** - Login history and audit trail

### Feature Tables:
- **messages** - Student-teacher messaging
- **quiz_questions** - Quiz content
- **student_performance** - Performance tracking
- **study_plans** - AI-generated study plans
- **payments** - Payment transactions
- **feedback** - User feedback

## Default Credentials
- **Admin Username**: admin
- **Admin Password**: admin2026 (bcrypt hashed in database)
- **Super Admin Override**: Newton / ##0000

## Security Features
- Bcrypt password hashing
- Login attempt limiting (default: 5 attempts)
- Account lockout (default: 24 hours)
- Session management
- Role-based access control

## Indexes
The schema includes indexes for common queries:
- Student and teacher username lookups
- Admin status queries
- Message queries by student/teacher
- Performance data queries

## Migration from SQLite
To migrate existing data from SQLite:

```python
import sqlite3
import psycopg2

# Read from SQLite
sqlite_conn = sqlite3.connect('data/mengo.db')
sqlite_cursor = sqlite_conn.cursor()

# Write to PostgreSQL
pg_conn = psycopg2.connect("postgresql://user:password@localhost/mengo_hub")
pg_cursor = pg_conn.cursor()

# Copy students
sqlite_cursor.execute('SELECT * FROM students')
for row in sqlite_cursor.fetchall():
    pg_cursor.execute('INSERT INTO students VALUES (...)', row)

pg_conn.commit()
```

## Backup and Recovery
```bash
# Backup
pg_dump mengo_hub > mengo_hub_backup.sql

# Restore
psql mengo_hub < mengo_hub_backup.sql
```
