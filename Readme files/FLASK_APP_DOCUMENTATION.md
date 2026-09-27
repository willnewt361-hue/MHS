# Mengo-Hub Flask Application Documentation

## Overview
The comprehensive Flask application (`flask_app.py`) is the core API server for the Mengo-Hub educational platform. It provides:

- **2000+ lines** of well-organized, production-ready code
- **24+ API endpoints** for all major features
- **3 WebSocket handlers** for real-time AI research
- **Advanced authentication** with certificate validation
- **Premium features** with AI integration
- **SSL/HTTPS support** for secure communication
- **Multiple email provider** support
- **Rate limiting** and security middleware
- **Comprehensive error handling** and logging

## Architecture
### Project Structure
```
mengo-hub-system/
├── flask_app.py                 # Main Flask application (2000+ lines)
├── ai_service.py                # AI provider integration
├── email_service.py             # Email provider integration  
├── premium_features.py          # Analytics and gamification
├── schema.sql                   # Database schema
├── requirements.txt             # Python dependencies
├── data/
│   ├── app.log                  # Application logs
│   ├── cert.pem                 # SSL certificate (generated)
│   ├── key.pem                  # SSL key (generated)
│   ├── past_papers/             # Uploaded past papers
│   └── attachments/             # File attachments
├── public/                      # Static files
│   ├── images/
│   │   ├── students/
│   │   └── teachers/
│   └── index.html
└── FLASK_APP_DOCUMENTATION.md   # This file
```

### Database Tables
- **students** - Student accounts, profiles, certificates
- **teachers** - Teacher accounts and subject assignments
- **quiz_questions** - Quiz questions with explanations
- **student_performance** - Performance tracking and analytics
- **study_plans** - AI-generated study plans
- **past_papers** - Past paper uploads and tracking
- **email_config** - Email provider configuration
- **admin_certificates** - Admin certificate management

## Configuration
### Environment Variables
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DEBUG=false

# Database
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/mengo_hub

# Admin Configuration
ADMIN_ID=A000
ADMIN_SECRET_KEY=Newton
ADMIN_SECRET_PASSWORD=##0000
ADMIN_API_TOKEN=MengoAdminAPIToken2026
SUPER_ADMIN_API_TOKEN=MengoSuperAdminToken2026

# SSL/HTTPS
USE_SSL=true
CERT_FILE=data/cert.pem
KEY_FILE=data/key.pem

# AI Provider (local, openai, anthropic)
AI_PROVIDER=local
LOCAL_MODEL=llama
LOCAL_AI_URL=http://localhost:8000
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Email Configuration
EMAIL_PROVIDER=gmail
EMAIL_SENDER=noreply@mengo-hub.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Security
LOGIN_ATTEMPTS_LIMIT=5
LOCKOUT_HOURS=24
RATE_LIMIT_CALLS=100
RATE_LIMIT_PERIOD=3600

# File Upload
MAX_UPLOAD_SIZE=52428800  # 50MB
```

## API Endpoints
### Authentication
#### POST /api/auth/login
Login user (student or teacher)
**Request:**
```json
{
  "username": "student_username",
  "password": "password",
  "role": "student"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "STU123",
    "username": "student_username",
    "fullName": "Student Name",
    "role": "student",
    "is_admin": 0
  }
}
```

#### POST /api/auth/logout
Logout current user
---
### Premium Features - Smart Revision
#### POST /api/premium/smart-revision
Generate AI-powered revision questions with UNEB patterns
**Request:**
```json
{
  "subject": "Mathematics",
  "difficulty": "hard",
  "count": 10,
  "context": "Optional study context"
}
```

**Response:**
```json
{
  "success": true,
  "questions": [
    {
      "question": "Question text...",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "explanation": "Explanation text...",
      "difficulty": "hard"
    }
  ],
  "subject": "Mathematics",
  "count": 10
}
```

---
### Premium Features - Weakness Detector
#### GET /api/premium/weakness-detector
AI-enhanced analysis of student weaknesses
**Response:**
```json
{
  "success": true,
  "analysis": {
    "weak_subjects": ["Mathematics", "Physics"],
    "recommendations": ["Practice more exercises", "Review fundamentals"],
    "focus_areas": ["Algebra", "Calculus"],
    "estimated_improvement_time": "4 weeks"
  },
  "performance_summary": {
    "total_attempts": 45,
    "subjects_attempted": ["Math", "English", "Science"]
  }
}
```

---
### Premium Features - Exam Predictor
#### GET /api/premium/exam-predictor?subject=Mathematics
Predict likely exam questions based on patterns
**Response:**
```json
{
  "success": true,
  "subject": "Mathematics",
  "prediction": {
    "predicted_topics": ["Algebra", "Geometry", "Trigonometry"],
    "question_types": ["Multiple choice", "Short answer"],
    "difficulty_distribution": {
      "easy": 20,
      "medium": 50,
      "hard": 30
    },
    "preparation_focus": "Focus on algebra and geometry"
  }
}
```

---
### Premium Features - Study Plan
#### POST /api/premium/study-plan
Generate AI-powered personalized study plan
**Request:**
```json
{
  "weaknesses": ["Algebra", "Essay writing"],
  "hours_per_day": 2.5
}
```

**Response:**
```json
{
  "success": true,
  "message": "Study plan generated",
  "plan": {
    "daily_schedule": [
      {
        "time": "09:00",
        "subject": "Mathematics",
        "activity": "Practice algebra problems",
        "duration_minutes": 45
      }
    ],
    "weekly_goals": ["Complete 20 algebra problems", "Write 2 essays"],
    "resources_needed": ["Textbook", "Online tutorials"],
    "revision_schedule": ["Day 5", "Day 10", "Day 20"],
    "assessment_checkpoints": ["End of week 1", "End of month"]
  }
}
```

#### GET /api/premium/study-plan
Retrieve existing study plan
---
### Premium Features - Quiz
#### GET /api/premium/quiz?subject=Mathematics&difficulty=medium
Get a random quiz question
**Response:**
```json
{
  "success": true,
  "question": {
    "id": 42,
    "subject": "Mathematics",
    "question": "What is 2 + 2?",
    "options": ["3", "4", "5", "6"],
    "difficulty": "medium"
  }
}
```

#### POST /api/premium/quiz
Submit answer and get feedback
**Request:**
```json
{
  "question_id": 42,
  "answer": "4"
}
```

**Response:**
```json
{
  "success": true,
  "is_correct": true,
  "correct_answer": "4",
  "explanation": "2 + 2 equals 4",
  "points_earned": 10
}
```

---
### Premium Features - Analytics
#### GET /api/premium/analytics/<student_id>
Get comprehensive student analytics
**Response:**
```json
{
  "success": true,
  "student_id": "STU123",
  "metrics": {
    "average": 75.5,
    "trend": "improving",
    "consistency": 85.2,
    "total_attempts": 50,
    "highest_score": 98,
    "lowest_score": 42
  },
  "by_subject": {
    "Mathematics": [
      {"score": 85, "total": 100, "percentage": 85}
    ]
  }
}
```

---
### Premium Features - Attendance
#### GET /api/premium/attendance
Get attendance information
**Response:**
```json
{
  "success": true,
  "student_id": "STU123",
  "attendance_rate": 95,
  "total_sessions": 100,
  "present": 95,
  "absent": 5
}
```

#### POST /api/premium/attendance
Record attendance
**Request:**
```json
{
  "action": "present"
}
```

---
### Premium Features - Gamification
#### GET /api/premium/gamification/<student_id>
Get gamification data (badges, points, achievements)
**Response:**
```json
{
  "success": true,
  "student_id": "STU123",
  "points": 450,
  "level": 3,
  "badges": [
    {"badge": "first_quiz", "name": "Quiz Starter", "icon": "🎯"},
    {"badge": "perfect_score", "name": "Perfect Score", "icon": "⭐"}
  ],
  "achievements": [
    "Completed first quiz",
    "Scored 100% on 3 quizzes"
  ]
}
```

---
### Premium Features - Past Papers
#### GET /api/premium/past-papers
List all past papers
**Response:**
```json
{
  "success": true,
  "papers": [
    {
      "id": 1,
      "subject": "Mathematics",
      "year": 2023,
      "difficulty": "hard",
      "score": 85,
      "file_path": "data/past_papers/math_2023.pdf"
    }
  ]
}
```

#### POST /api/premium/past-papers
Upload past paper
**Request:** (multipart/form-data)
```
file: [PDF file]
subject: "Mathematics"
year: 2023
difficulty: "hard"
```

#### DELETE /api/premium/past-papers?id=1
Delete past paper
---
### Premium Features - Reports
#### GET /api/premium/reports/<student_id>
Generate comprehensive progress report
**Response:**
```json
{
  "success": true,
  "report": {
    "student_id": "STU123",
    "generated_at": "2024-01-15T10:30:00",
    "overall_performance": 75,
    "subjects": {"Math": 80, "English": 70},
    "strengths": ["Consistent participation"],
    "areas_for_improvement": ["Time management"],
    "study_consistency": 85,
    "recommendation": "Student is making good progress..."
  }
}
```

---
### Premium Features - Content Summarization
#### POST /api/premium/summarize
Summarize educational content using AI
**Request:**
```json
{
  "content": "Long educational text to summarize...",
  "max_length": 200
}
```

**Response:**
```json
{
  "success": true,
  "original_length": 500,
  "summary": "Concise summary of content...",
  "summary_length": 45
}
```

---
### WebSocket Endpoints - AI Research
#### Socket.IO: ai_research_query
Query AI for research streaming
**Request:**
```json
{
  "query": "Explain quantum mechanics",
  "student_id": "STU123",
  "subject": "Physics"
}
```

**Stream responses:**
- `ai_research_chunk` - Chunks of response text
- `ai_research_complete` - Final response status
---

### Admin Endpoints - Email Configuration
#### GET /api/admin/email-config
Get current email configuration (requires admin token)
**Response:**
```json
{
  "success": true,
  "config": {
    "provider": "gmail",
    "sender_email": "noreply@mengo-hub.com",
    "sender_name": "Mengo-Hub",
    "is_active": true
  }
}
```

#### POST /api/admin/email-config
Set email configuration (requires super admin token)
**Request:**
```json
{
  "provider": "gmail",
  "sender_email": "noreply@mengo-hub.com",
  "sender_name": "Mengo-Hub",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "api_key": "optional-api-key"
}
```

#### POST /api/admin/email-config/test
Test email configuration
**Request:**
```json
{
  "email": "test@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test email sent to test@example.com"
}
```

---

### Admin Endpoints - Alerts
#### POST /api/admin/send-admin-alert
Send alerts to administrators
**Request:**
```json
{
  "title": "System Alert",
  "message": "Alert message content",
  "recipient": "admin@mengo.com"
}
```

---
### Admin Endpoints - Certificate Management
#### GET /api/admin/certificate
Get admin certificate status
**Response:**
```json
{
  "success": true,
  "has_certificate": true,
  "verified": 1,
  "is_valid": true,
  "issuer": "Self-signed",
  "expiry_date": "2025-01-15"
}
```

#### POST /api/admin/certificate
Upload admin certificate
**Request:** (multipart/form-data)
```
file: [Certificate file]
issuer: "Certificate issuer name"
```

---
### Admin Endpoints - Authentication
#### POST /api/admin/auth
Admin authentication with certificate validation
**Request:**
```json
{
  "admin_id": "A000",
  "password": "admin_password",
  "certificate": "optional_certificate_data"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Admin authentication successful",
  "admin": {
    "id": "A000",
    "username": "admin_username",
    "fullName": "Administrator Name"
  }
}
```

---
### Admin Endpoints - CSV Import
#### POST /api/import-csv
Import users from CSV file
**Request:**
```json
{
  "import_password": "ImportPassword2026",
  "csv_path": "data/import.csv"
}
```

**Response:**
```json
{
  "success": true,
  "imported": 45,
  "skipped": 3,
  "imported_users": [...],
  "skipped_users": [...]
}
```

---
### System Endpoints
#### GET /api/health
Health check endpoint
**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00"
}
```

#### GET /api/status
System status and version
**Response:**
```json
{
  "success": true,
  "app_name": "Mengo-Hub",
  "version": "1.0.0",
  "environment": "production",
  "ai_provider": "local",
  "email_provider": "gmail",
  "timestamp": "2024-01-15T10:30:00"
}
```

---
## Authentication & Security
### Token-Based Authentication
The application uses Bearer token authentication for admin endpoints:
```
Authorization: Bearer <TOKEN>
```

#### Token Types:
- **ADMIN_API_TOKEN** - Regular admin access
- **SUPER_ADMIN_API_TOKEN** - Super admin with all privileges

### Certificate Validation
**Fixed Issue:** The application now properly handles certificate validation:
1. **Null certificates allowed** - Legacy admins without certificates can still authenticate
2. **Valid certificates checked** - Admins with certificates must have verified, non-expired certificates
3. **Graceful fallback** - System works with or without certificate requirements

### Password Security
- Passwords hashed with **bcrypt** (salt rounds: 12)
- Password verification uses secure comparison
- Failed login attempts tracked (prevents brute force)
- Account lockout after 5 failed attempts (24 hours)

### Session Management
- Flask sessions with secure cookies
- Session data includes: user_id, username, role, is_admin
- Sessions cleared on logout
- Session timeout: 24 hours (configurable)

---
## Error Handling
All endpoints return consistent JSON responses:
### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...}
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description"
}
```

### HTTP Status Codes
- **200** - OK
- **201** - Created
- **400** - Bad Request
- **401** - Unauthorized
- **403** - Forbidden
- **404** - Not Found
- **500** - Server Error

---
## Logging
Application logs are written to `data/app.log` with the following format:
```
2024-01-15 10:30:00,000 - flask_app - INFO - Login successful for user STU123
2024-01-15 10:31:00,000 - flask_app - ERROR - Quiz error: Database connection failed
```

### Log Levels:
- **INFO** - Normal operations
- **WARNING** - Potential issues
- **ERROR** - Application errors
- **DEBUG** - Detailed debugging info

---
## WebSocket Integration
Real-time features using Socket.IO:
### Connection Events
- `connect` - Client connects
- `disconnect` - Client disconnects

### AI Research Events
- `ai_research_query` - Send research query
- `ai_research_chunk` - Receive response chunks (streaming)
- `ai_research_complete` - Research query completed

### Usage Example (JavaScript)
```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to AI Research server');
});

socket.emit('ai_research_query', {
  query: 'Explain machine learning',
  student_id: 'STU123',
  subject: 'Computer Science'
});

socket.on('ai_research_chunk', (data) => {
  console.log('Received:', data.chunk);
});

socket.on('ai_research_complete', (data) => {
  console.log('Research completed:', data);
});
```

---
## Production Deployment
### Recommended Configuration
```python
# production settings
DEBUG = False
TESTING = False
USE_SSL = True
DATABASE_TYPE = 'postgresql'
ENVIRONMENT = 'production'
```

### WSGI Server
Use Gunicorn for production:
```bash
pip install gunicorn
gunicorn --workers 4 --worker-class eventlet -w 1 flask_app:app
```

### Reverse Proxy
Use Nginx to proxy requests:
```nginx
server {
    listen 80;
    server_name mengo-hub.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database
- **PostgreSQL** recommended for production
- Connection pooling: 10-20 connections
- Backup strategy: Daily snapshots
- Replication: Master-slave for HA

### Security Headers

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---
## Performance Optimization
### Caching
```python
# Cache frequently accessed data
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)
def get_leaderboard():
    # Cached for 5 minutes
    pass
```

### Database Optimization
- Index frequently queried columns
- Use prepared statements
- Connection pooling with psycopg2
- Query optimization with EXPLAIN ANALYZE

### API Rate Limiting
```python
@rate_limit
@app.route('/api/endpoint')
def rate_limited_endpoint():
    # Rate limited to 100 calls per hour
    pass
```

---
## Testing
### Unit Tests
```python
def test_login():
    response = client.post('/api/auth/login', json={
        'username': 'test_user',
        'password': 'password',
        'role': 'student'
    })
    assert response.status_code == 200
    assert response.json['success'] == True
```

### Integration Tests
Test full workflows with real database:
```python
def test_quiz_workflow():
    # Login
    # Get question
    # Submit answer
    # Verify points awarded
```

---
## Troubleshooting
### Common Issues
**1. SSL Certificate Error**
```
Solution: Run generate_certificate() or set USE_SSL=false
```

**2. Database Connection Failed**
```
Solution: Check DATABASE_URL and ensure PostgreSQL is running
```

**3. Email Not Sending**
```
Solution: Verify EMAIL_PROVIDER, SMTP credentials, and app passwords
```

**4. AI Service Not Responding**
```
Solution: Check AI_PROVIDER and LOCAL_AI_URL for local models
```

**5. WebSocket Connection Failed**
```
Solution: Ensure SocketIO is configured and client has correct URL
```

---
## Support & Documentation
- API Docs: See this document
- Schema: See `schema.sql`
- Environment: See `.env.example`
- Deployment: See `PRODUCTION_README.md`
- Email Setup: See `EMAIL_SETUP_GUIDE.md`
- HTTPS Setup: See `HTTPS_SETUP_LOCAL.md`

---
## Version History
**v1.0.0** (Current)
- Complete Flask application with all premium features
- AI integration with local and cloud providers
- Real-time WebSocket communication
- Certificate-based admin authentication
- Email provider integration
- Comprehensive logging and error handling

---
## License
Mengo-Hub System © 2024. All rights reserved.

---
**Last Updated:** January 15, 2024  
**Maintainer:** Mengo-Hub Development Team
