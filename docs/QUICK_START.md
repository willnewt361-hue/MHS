# Mengo-Hub Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (defaults should work for local development)
```

### Step 3: Initialize System
```bash
python SETUP_AND_FIX.py
```

Expected output:
```
============================================================
Mengo-Hub System Setup and Fix
============================================================

--- Connecting to Database ---
✓ Connected to postgresql database

--- Verifying Admin User ---
✓ Admin user A000 already exists

--- Creating Admin Certificate ---
✓ Created permanent admin certificate for A000
  Certificate expires: 2036-06-03 18:15:23.572000

--- Organizing Project Structure ---
✓ Created src/services/
✓ Created src/routes/
... (more folders)

--- Testing Login Functionality ---
Testing admin login...
✓ Admin login works: Logged in as Newton (Admin Override)

============================================================
Setup Complete!
============================================================
```

### Step 4: Start the Application
```bash
python run.py
```

The application will start on `http://localhost:5000`

---

## 🔐 Login Information

### Admin Account
- **Username**: `Newton`
- **Password**: `##0000`
- **Dashboard**: `http://localhost:5000/admin/dashboard`

---

## 📝 Test CSV Import

### 1. Create Sample CSV File
Create `data/imports/import.csv`:
```csv
type,id,username,password,fullName,email,stream,class,role,is_admin,payment_status
student,S001,alice_wonder,pass123,Alice Wonder,alice@example.com,North,S1,Student,0,paid
student,S002,bob_builder,pass456,Bob Builder,bob@example.com,South,S2,Student,0,paid
teacher,T001,prof_smith,pass789,Prof. Smith,smith@example.com,East,S3,Teacher,0,paid
```

### 2. Import Users (via API)
```bash
curl -X POST http://localhost:5000/api/import-csv \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -H "Content-Type: application/json" \
  -d '{
    "import_password": "ImportPassword2026",
    "csv_path": "data/imports/import.csv"
  }'
```

---

## ✅ Verify Everything Works

### 1. Admin Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "Newton",
    "password": "##0000"
  }'
```

### 2. Regular User Login (after CSV import)
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_wonder",
    "password": "pass123"
  }'
```

### 3. Get Admin Logs
```bash
curl http://localhost:5000/api/logs \
  -H "Authorization: Bearer MengoAdminAPIToken2026"
```

---

## 🛠 Troubleshooting

### Database Connection Error
```
ERROR: Failed to connect to database
```
**Solution**: Make sure PostgreSQL is running and DATABASE_URL is correct in .env

### Port Already in Use
```
Address already in use
```
**Solution**: Change Flask port in run.py or kill existing process

### CSV Import Not Working
**Check**: 
- Admin token is valid: `MengoAdminAPIToken2026`
- Import password is correct: `ImportPassword2026`
- CSV file exists at specified path

---

## 📊 Project Structure

```
Mengo-Hub-System/
├── flask_app.py              # Main Flask application
├── run.py                    # Application entry point
├── SETUP_AND_FIX.py         # System initialization
├── SYSTEM_SETUP_README.md   # Detailed documentation
├── QUICK_START.md           # This file
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
│
├── src/
│   ├── services/            # Business logic
│   ├── routes/              # API routes
│   ├── utils/               # Utilities
│   └── middleware/          # Middleware
│
├── config/                  # Configuration files
├── templates/               # HTML templates
├── public/                  # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── data/                    # Data and imports
│   └── imports/
│
├── uploads/                 # User uploads
│   ├── documents/
│   ├── audio/
│   ├── videos/
│   └── images/
│
├── logs/                    # Application logs
└── tests/                   # Test files
```

---

## 📚 Key Features Working

✅ Admin user authentication
✅ CSV bulk import for students/teachers
✅ User role-based access
✅ Admin dashboard
✅ Audit logging
✅ Certificate management
✅ API authentication tokens

---

## 🎯 Next Steps

1. ✅ System is running
2. Test all features in browser
3. Create sample data
4. Configure email (optional)
5. Set up payment gateway (optional)
6. Deploy to production

---

## 💡 Tips

- View logs: `tail -f logs/mengo-hub.log`
- Reset database: Delete `data/mengo.db` and re-run SETUP_AND_FIX.py
- Change admin password: Edit .env and run SETUP_AND_FIX.py
- View API docs: Check SYSTEM_SETUP_README.md for all endpoints

---

**Ready to build? Start with:** `python run.py` 🚀
