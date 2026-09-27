# Mengo-Hub System - Setup & Fixes

## Quick Start

### 1. Clone/Setup Repository
```bash
cd Mengo-Hub-System
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Setup Script
```bash
python SETUP_AND_FIX.py
```

This will:
- Create/verify admin user (A000)
- Generate permanent admin certificate
- Initialize database tables
- Organize project structure
- Test login functionality

### 4. Start Application
```bash
python run.py
```

---

## Fixed Issues

### ✅ Issue 1: Admin Login Not Being Logged
**Problem**: User A000 admin logins were appearing in audit logs  
**Solution**: Modified `log_action()` function to skip logging A000 admin logins

### ✅ Issue 2: CSV Import Credentials Not Working
**Problem**: Only A000 admin could login; regular users from CSV failed  
**Solution**: Fixed login endpoint to allow regular users without requiring `is_admin=1` when no role specified

### ✅ Issue 3: Admin Certificate System
**Problem**: Admin certificate validation was blocking admin access  
**Solution**: 
- Created permanent admin certificate for A000 (10-year validity)
- Certificate stored in `super_admin_certificates` table
- All admins can now access dashboard without certificate redirect loops

### ✅ Issue 4: Project Organization
**Solution**: Created organized project structure:
```
src/
  ├── services/        # Business logic
  ├── routes/          # API endpoints
  ├── utils/           # Helper functions
  └── middleware/      # Flask middleware
config/                # Configuration files
templates/             # HTML templates
public/                # Static files (CSS, JS)
data/                  # Data and imports
logs/                  # Application logs
uploads/               # User uploads
tests/                 # Test files
docs/                  # Documentation
```

---

## Admin User Access

### Login Credentials
- **Username**: `Newton` (ADMIN_SECRET_KEY)
- **Password**: `##0000` (ADMIN_SECRET_PASSWORD)
- **User ID**: `A000` (ADMIN_ID)

### Admin Certificate
- **Validity**: 10 years (3650 days)
- **Storage**: `super_admin_certificates` table
- **Auto-generated on setup**: Yes

### Admin Features
- Dashboard access
- User management
- CSV bulk import
- System configuration
- Audit logging (exempt from own logins)

---

## Feature Testing

### Test CSV Import
1. Create `data/imports/import.csv` with user data:
```csv
type,id,username,password,fullName,email,stream,class,role,is_admin,payment_status,certificate
student,S001,john_doe,password123,John Doe,john@example.com,East,S1,Student,0,paid,
student,S002,jane_smith,password456,Jane Smith,jane@example.com,West,S2,Student,0,paid,
teacher,T001,mr_math,password789,Mr. Math,math@example.com,North,S3,Teacher,0,paid,
```

2. Call import endpoint:
```bash
curl -X POST http://localhost:5000/api/import-csv \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -H "Content-Type: application/json" \
  -d '{
    "import_password": "ImportPassword2026",
    "csv_path": "data/imports/import.csv"
  }'
```

### Test Admin Dashboard
1. Login as admin: `Newton` / `##0000`
2. Access: `http://localhost:5000/admin/dashboard`
3. Verify no certificate redirects

### Test Regular User Login
1. Import a user via CSV
2. Login with imported credentials (username + password)
3. No role required - auto-detects student/teacher

---

## Database Schema

### Key Tables for Admin/Auth
- `students` - Contains admin users and regular students
- `teachers` - Teacher accounts
- `super_admin_certificates` - Admin access certificates
- `audit_logs` - System audit trail (excludes A000 logins)
- `loginLogs` - Login history

### Admin Certificate Fields
```sql
CREATE TABLE super_admin_certificates (
    id SERIAL PRIMARY KEY,
    certificate_id VARCHAR(100) UNIQUE,
    admin_id VARCHAR(50),           -- References students.id
    certificate_code VARCHAR(255),  -- Certificate hash
    issued_at TIMESTAMP,
    expires_at TIMESTAMP,           -- 10 years for A000
    is_active INTEGER,
    is_revoked INTEGER,
    issued_by VARCHAR(50)
);
```

---

## Troubleshooting

### Issue: "Admin certificate required"
**Solution**: Run `python SETUP_AND_FIX.py` to regenerate certificate

### Issue: Regular users can't login
**Solution**: Ensure CSV import worked, check `students`/`teachers` table for user

### Issue: A000 appearing in audit logs
**Solution**: Already fixed. Make sure you're running the updated code.

### Issue: Database connection fails
**Solution**: Check DATABASE_URL in .env and ensure PostgreSQL is running

---

## Admin API Endpoints

### Login
```bash
POST /api/login
Content-Type: application/json
{
  "username": "Newton",
  "password": "##0000"
}
```

### CSV Import
```bash
POST /api/import-csv
Authorization: Bearer MengoAdminAPIToken2026
{
  "import_password": "ImportPassword2026",
  "csv_path": "data/imports/import.csv"
}
```

### Admin Dashboard
```bash
GET /admin/dashboard
Authorization: Bearer MengoAdminAPIToken2026
```

### Get Audit Logs
```bash
GET /api/logs
Authorization: Bearer MengoAdminAPIToken2026
```

---

## Environment Variables (Key)

| Variable | Default | Purpose |
|----------|---------|---------|
| ADMIN_ID | A000 | Super admin user ID |
| ADMIN_SECRET_KEY | Newton | Admin username |
| ADMIN_SECRET_PASSWORD | ##0000 | Admin password |
| DATABASE_TYPE | postgresql | DB type |
| DATABASE_URL | postgresql://... | DB connection |
| ADMIN_IMPORT_PASSWORD | ImportPassword2026 | CSV import auth |
| LOGIN_ATTEMPTS_LIMIT | 5 | Failed login limit |
| LOCKOUT_HOURS | 24 | Account lockout duration |

---

## Next Steps

1. ✅ Setup complete
2. 🔄 Review all features in admin dashboard
3. 📊 Test analytics and reporting
4. 🎓 Test student features
5. 👨‍🏫 Test teacher features
6. 📝 Create sample data for demo
7. 🚀 Deploy to production

---

## Support

For issues or questions:
1. Check logs: `logs/mengo-hub.log`
2. Review this README
3. Check `.env` configuration
4. Verify database is running

---

**System Setup Complete!** 🎉
