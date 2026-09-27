# MENGO-HUB QUICK REFERENCE CARD
## 🚀 START SERVER (30 SECONDS)
**Windows:**
```batch
run_local_https.bat
```

**Linux/Mac:**
```bash
bash run_local_https.sh
```

**Manual (All):**
```bash
pip install -r requirements.txt
python flask_app.py
```

## 🌐 ACCESS
```
URL: https://localhost:5000/
Admin: admin / ##0000
```

---
## 💡 TOP FEATURES
### For Students
**1️⃣ Get AI Revision Questions**
```bash
curl -X POST https://localhost:5000/api/premium/smart-revision \
  -H "X-User-ID: S001" \
  -H "Content-Type: application/json" \
  -d '{"student_id":"S001","subject":"Mathematics","difficulty":"hard"}'
```

**2️⃣ Find Weak Areas**
```bash
curl https://localhost:5000/api/premium/weakness-detector?student_id=S001 \
  -H "X-User-ID: S001"
```

**3️⃣ Take Quiz & Get Score**
```bash
curl -X POST https://localhost:5000/api/premium/quiz \
  -H "X-User-ID: S001" \
  -d '{"student_id":"S001","subject":"Math","answers":[...]}'
```

**4️⃣ See Your Progress**
```bash
curl https://localhost:5000/api/premium/analytics/S001 \
  -H "X-User-ID: S001"
```

**5️⃣ Chat with AI**
```bash
curl -X POST https://localhost:5000/api/premium/ai-chat \
  -H "X-User-ID: S001" \
  -d '{"student_id":"S001","message":"Explain photosynthesis"}'
```

### For Admins

**1️⃣ Record Attendance**
```bash
curl -X POST https://localhost:5000/api/premium/attendance \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -d '{"student_id":"S001","date":"2026-05-10","status":"present"}'
```

**2️⃣ Test Email**
```bash
curl -X POST https://localhost:5000/api/admin/email-config/test \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -d '{"to_email":"admin@mengo.com"}'
```

**3️⃣ Send Admin Alert**
```bash
curl -X POST https://localhost:5000/api/admin/send-admin-alert \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -d '{"title":"Update","message":"New version","severity":"info"}'
```

---

## 📧 EMAIL SETUP (2 MINUTES)
1. Go to: https://myaccount.google.com/apppasswords
2. Get 16-char password
3. Update .env:
```
EMAIL_PROVIDER=gmail
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=16-char-password
```
4. Test: Run test email endpoint above
---
## 🤖 AI SETUP (CHOOSE ONE)
### Local (Free)
```
AI_PROVIDER=local
LOCAL_MODEL=llama
LOCAL_AI_URL=http://localhost:8000
```

### OpenAI (Paid)
```
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

### Anthropic (Paid)
```
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
```

---
## 🔌 WEBSOCKET AI (Real-Time)
**JavaScript Client:**
```javascript
const socket = io('https://localhost:5000', {path: '/socket.io'});

// Start research
socket.emit('research_start', {
  student_id: 'S001',
  topic: 'Photosynthesis',
  subject: 'Biology'
});

// Get AI response
socket.emit('ai_query', {
  session_id: 'SESSION_ID',
  query: 'What is photosynthesis?'
});

socket.on('ai_response', (data) => {
  console.log(data.response);
});

// Generate questions
socket.emit('generate_questions', {
  session_id: 'SESSION_ID',
  subject: 'Biology',
  topic: 'Photosynthesis',
  difficulty: 'hard',
  count: 5
});

socket.on('questions_generated', (data) => {
  console.log(data.questions);
});
```

---
## 📊 DATABASE
**All tables created automatically on first run**
Key tables:
- `students` - Student accounts
- `teachers` - Teacher accounts
- `student_performance` - Quiz scores
- `attendance` - Attendance records
- `student_badges` - Achievements
- `study_plans` - AI study schedules
- `ai_chat_messages` - AI conversations
- `email_configuration` - Email settings

---
## 🔑 IMPORTANT CREDENTIALS
```
Default Admin:
  ID: A000
  Username: admin
  Password: ##0000

Admin API Token: MengoAdminAPIToken2026
Super Admin Token: MengoSuperAdminToken2026
```

---
## ⚙️ ENVIRONMENT VARIABLES
Most important:
```
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@localhost:5432/mengo_hub

EMAIL_PROVIDER=gmail
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=app-password

AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

See `.env.example` for all options.
---

## 🐛 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "Port 5000 in use" | `taskkill /PID <pid> /F` or change PORT |
| "SSL not found" | Run `openssl` command to generate cert.pem |
| "Email not sending" | Check .env EMAIL settings, test endpoint |
| "AI not responding" | Verify AI_PROVIDER and keys in .env |
| "WebSocket timeout" | Check firewall allows port 5000 |
| "Certificate error" | Normal for self-signed, click Advanced/Proceed |

---

## 📚 FEATURES SUMMARY

✅ 15 Premium Features  
✅ 60+ API Endpoints  
✅ Real-time WebSocket AI  
✅ Multi-provider Email  
✅ Local & Cloud AI  
✅ Gamification System  
✅ Analytics Dashboard  
✅ HTTPS/SSL Support  
✅ Admin Management  
✅ Attendance Tracking  

---
## 📖 DOCUMENTATION
- `COMPLETE_IMPLEMENTATION_GUIDE.md` - Full API docs
- `EMAIL_SETUP_GUIDE.md` - Email setup
- `HTTPS_SETUP_LOCAL.md` - SSL/HTTPS
- `IMPLEMENTATION_COMPLETE.md` - What was done
- `PRODUCTION_README.md` - Deployment

---
## 🎯 COMMON TASKS
### Add a Student
Use admin panel or `/api/import-csv`

### Create Quiz
Add to `quiz_questions` table

### Award Badge
`POST /api/premium/gamification` with badge_key

### Generate Report
`GET /api/premium/reports/{student_id}`

### Research Topic
WebSocket: `research_topic` event

### Create Study Plan
`POST /api/premium/study-plan` endpoint

---

## 🚀 PRODUCTION DEPLOYMENT

1. Install Gunicorn: `pip install gunicorn`
2. Get certificate from Let's Encrypt
3. Set `DEBUG=False` in .env
4. Use production database (PostgreSQL)
5. Use production email (SendGrid)
6. Use production AI (OpenAI/Claude)
7. Run: `gunicorn -w 4 flask_app:app`

---
## ✅ READY TO GO!
Your Mengo-Hub system is now COMPLETE with:
- All 15 premium features
- Full AI integration
- Email system
- HTTPS support
- WebSocket real-time features
- Admin controls
- Analytics
- Gamification

**Start with**: `run_local_https.bat` (Windows) or `bash run_local_https.sh` (Linux)

**Access**: https://localhost:5000/

**Enjoy!** 🎊

---
*Version 2.0 Complete - May 10, 2026*
