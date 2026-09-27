# MENGO-HUB - Complete Implementation Guide
## 🚀 Quick Start
### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (email, AI provider, database)
```

### 3. Generate SSL Certificate (For HTTPS)
```batch
# Windows
run_local_https.bat

# Linux/Mac
./run_local_https.sh
```

### 4. Start the Server
```bash
# With SSL (HTTPS)
python flask_app.py

# Or use the Windows batch file
run_local_https.bat
```

### 5. Access Mengo-Hub
```
https://localhost:5000/
(Accept SSL certificate warning)

Default Admin:
- Username: admin
- Password: ##0000
```
---
## 📋 Premium Features Guide
### 1. Smart Revision (AI-Powered)
**Endpoint**: `POST /api/premium/smart-revision`
Generates UNEB-pattern exam questions with AI.
```bash
curl -X POST https://localhost:5000/api/premium/smart-revision \
  -H "X-User-ID: S001" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "subject": "Mathematics",
    "difficulty": "hard"
  }'
```

### 2. Weakness Detector
**Endpoint**: `GET /api/premium/weakness-detector`
Analyzes student performance to identify weak areas.
```bash
curl -X GET 'https://localhost:5000/api/premium/weakness-detector?student_id=S001' \
  -H "X-User-ID: S001"
```

**Response**:
```json
{
  "success": true,
  "weaknesses": ["Algebra", "Geometry"],
  "recommendations": ["Practice more on algebraic equations", "Review geometry theorems"],
  "focus_areas": ["Quadratic equations", "Coordinate geometry"],
  "estimated_improvement_time": "4 weeks"
}
```

### 3. Exam Predictor
**Endpoint**: `GET /api/premium/exam-predictor`
Predicts likely exam questions based on patterns.
```bash
curl -X GET 'https://localhost:5000/api/premium/exam-predictor?student_id=S001&subject=Mathematics' \
  -H "X-User-ID: S001"
```

### 4. Personalized Study Plans
**Endpoint**: `POST /api/premium/study-plan`
Generates AI-created study schedules.
```bash
curl -X POST https://localhost:5000/api/premium/study-plan \
  -H "X-User-ID: S001" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "weaknesses": ["Algebra", "Grammar"],
    "hours_per_day": 2
  }'
```

### 5. Interactive Quiz
**Endpoint**: `GET/POST /api/premium/quiz`
Dynamic quizzes with real-time scoring.
```bash
# Get quiz
curl -X GET 'https://localhost:5000/api/premium/quiz?subject=Mathematics&difficulty=medium&count=10' \
  -H "X-User-ID: S001"

# Submit answers
curl -X POST https://localhost:5000/api/premium/quiz \
  -H "X-User-ID: S001" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "subject": "Mathematics",
    "answers": [
      {"question_id": 1, "answer": "A", "correct": true},
      {"question_id": 2, "answer": "C", "correct": false}
    ]
  }'
```

### 6. Progress Analytics
**Endpoint**: `GET /api/premium/analytics/:student_id`
Comprehensive performance tracking.
```bash
curl -X GET 'https://localhost:5000/api/premium/analytics/S001' \
  -H "X-User-ID: S001"
```

**Response**:
```json
{
  "success": true,
  "performance_metrics": {
    "average": 78.5,
    "trend": "improving",
    "consistency": 85.2,
    "total_attempts": 15,
    "highest_score": 95,
    "lowest_score": 65
  },
  "attendance_percentage": 92.5,
  "subjects": ["Mathematics", "English", "Science"]
}
```

### 7. Attendance Tracker (Admin)
**Endpoint**: `GET/POST /api/premium/attendance`
Automated attendance monitoring.
```bash
# Record attendance
curl -X POST https://localhost:5000/api/premium/attendance \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "date": "2026-05-10",
    "status": "present"
  }'

# Get attendance records
curl -X GET 'https://localhost:5000/api/premium/attendance?student_id=S001' \
  -H "Authorization: Bearer MengoAdminAPIToken2026"
```

### 8. Gamification (Motivation Engine)
**Endpoint**: `GET /api/premium/gamification/:student_id`
Points, badges, leaderboards.
```bash
curl -X GET 'https://localhost:5000/api/premium/gamification/S001' \
  -H "X-User-ID: S001"
```

**Response**:
```json
{
  "success": true,
  "total_points": 450,
  "badges": [
    {"badge_name": "Quiz Starter", "badge_key": "first_quiz"},
    {"badge_name": "Perfect Score", "badge_key": "perfect_score"}
  ],
  "leaderboard_position": 3
}
```

### 9. Past Papers Practice
**Endpoint**: `GET/POST /api/premium/past-papers`
Interactive practice with past exam papers.
```bash
# Get available papers
curl -X GET 'https://localhost:5000/api/premium/past-papers?subject=Mathematics' \
  -H "X-User-ID: S001"

# Submit attempt
curl -X POST https://localhost:5000/api/premium/past-papers \
  -H "X-User-ID: S001" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "paper_id": 5,
    "score": 82.5,
    "total_score": 100,
    "duration_minutes": 120
  }'
```

### 10. Report Generation
**Endpoint**: `GET /api/premium/reports/:student_id`
Comprehensive academic reports.
```bash
curl -X GET 'https://localhost:5000/api/premium/reports/S001' \
  -H "X-User-ID: S001"
```

### 11. AI Summarizer
**Endpoint**: `POST /api/premium/summarize`
AI-powered content summarization.
```bash
curl -X POST https://localhost:5000/api/premium/summarize \
  -H "X-User-ID: S001" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Long text to summarize...",
    "max_length": 200
  }'
```

### 12. AI Chat Assistant
**Endpoint**: `POST /api/premium/ai-chat`
Real-time AI learning support.
```bash
curl -X POST https://localhost:5000/api/premium/ai-chat \
  -H "X-User-ID: S001" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "message": "Explain quadratic equations",
    "context": "mathematics"
  }'
```

---
## 🔌 WebSocket AI Features
### Real-Time AI Research Sessions
Connect WebSocket client:
```javascript
// Connect to AI namespace
const socket = io('https://localhost:5000', {
  path: '/socket.io',
  reconnection: true
});

// Join AI research namespace
socket.emit('connect', null);
socket.on('response', (data) => console.log(data));
```

### Start Research Session
```javascript
socket.emit('research_start', {
  student_id: 'S001',
  topic: 'Photosynthesis',
  subject: 'Biology'
});

socket.on('research_started', (data) => {
  console.log('Session started:', data.session_id);
});
```

### Query AI
```javascript
socket.emit('ai_query', {
  session_id: 'SESSION_ID',
  query: 'What is the role of chloroplasts in photosynthesis?'
});

socket.on('ai_response', (data) => {
  console.log('AI Response:', data.response);
});
```

### Research a Topic
```javascript
socket.emit('research_topic', {
  session_id: 'SESSION_ID',
  topic: 'Photosynthesis',
  depth: 'deep'  // 'shallow', 'moderate', 'deep'
});

socket.on('research_results', (data) => {
  console.log('Research data:', data.data);
});
```

### Generate Questions
```javascript
socket.emit('generate_questions', {
  session_id: 'SESSION_ID',
  subject: 'Biology',
  topic: 'Photosynthesis',
  difficulty: 'hard',
  count: 5
});

socket.on('questions_generated', (data) => {
  console.log('Questions:', data.questions);
});
```

### Generate Study Plan
```javascript
socket.emit('generate_study_plan', {
  session_id: 'SESSION_ID',
  student_id: 'S001',
  weaknesses: ['Cellular Biology', 'Genetics'],
  hours_per_day: 2.5
});

socket.on('study_plan_generated', (data) => {
  console.log('Study plan:', data.study_plan);
});
```

---
## 📧 Email Configuration
### Setup Gmail (Free - Recommended for Testing)
1. Enable 2FA: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Update `.env`:
```
EMAIL_PROVIDER=gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_SENDER=your-email@gmail.com
EMAIL_SENDER_NAME=Mengo-Hub System
```

### Test Email Configuration
**Endpoint**: `POST /api/admin/email-config/test`
```bash
curl -X POST https://localhost:5000/api/admin/email-config/test \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -H "Content-Type: application/json" \
  -d '{"to_email": "admin@mengo.com"}'
```

### Configure Email in Admin
**Endpoint**: `POST /api/admin/email-config`
```bash
curl -X POST https://localhost:5000/api/admin/email-config \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": "A000",
    "provider": "gmail",
    "config": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "sender_email": "noreply@mengo-hub.com"
    }
  }'
```

### Send Admin Alert
**Endpoint**: `POST /api/admin/send-admin-alert`
```bash
curl -X POST https://localhost:5000/api/admin/send-admin-alert \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "System Update Available",
    "message": "A new version is available. Please update.",
    "severity": "warning"
  }'
```

---
## 🤖 AI Configuration
### Local AI (LLAMA/GPTAll - Free)
```
AI_PROVIDER=local
LOCAL_MODEL=llama
LOCAL_AI_URL=http://localhost:8000
```

### Production AI - OpenAI (Paid)
```
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
AI_MODEL=gpt-4  # or gpt-3.5-turbo
```

### Production AI - Anthropic (Paid)
```
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-key
```

---
## 🔒 Certificate & Admin Access Fix
The certificate blocking issue has been FIXED. Admins are now determined by:
- `is_admin = 1` flag (primary)
- `certificate` field (optional, not blocking)
**Verify Admin Access**:
```bash
curl -X GET 'https://localhost:5000/api/admin/validate-certificate?user_id=A000' \
  -H "Authorization: Bearer MengoAdminAPIToken2026"
```

---
## 📚 Database Schema
New tables added for premium features:
- `attendance` - Student attendance records
- `student_points` - Gamification points
- `student_badges` - Achievement badges
- `past_papers` - Exam practice materials
- `past_paper_attempts` - Practice session records
- `research_sessions` - AI research sessions
- `ai_chat_messages` - AI conversation logs
- `email_configuration` - Email provider settings
- `system_settings` - Global system configuration

---
## 🧪 Testing Checklist
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create .env from .env.example
- [ ] Generate SSL certificate
- [ ] Run migrations: `python flask_app.py` (initializes DB)
- [ ] Access https://localhost:5000/
- [ ] Login with admin credentials
- [ ] Test Smart Revision endpoint
- [ ] Test WeaknessDetector endpoint
- [ ] Test Quiz submission
- [ ] Configure email and send test email
- [ ] Connect WebSocket and start research session
- [ ] Test AI responses
- [ ] Check attendance tracking
- [ ] View gamification stats
- [ ] Generate reports

---
## 🚀 Deployment
For production:
1. Use Let's Encrypt for certificates
2. Use SendGrid/AWS SES for emails
3. Use OpenAI/Claude for AI
4. Enable PostgreSQL
5. Set `DEBUG=False` in .env
6. Use production WSGI server (Gunicorn, uWSGI)

Example with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem flask_app:app
```

---
## 📞 Support
For issues, check:
1. ERROR_LOGS in console output
2. Database connectivity
3. Email provider configuration
4. SSL certificates exist
5. All requirements installed

---

**Status**: ✅ All premium features implemented
**Last Updated**: May 10, 2026
**Version**: 2.0 Complete
