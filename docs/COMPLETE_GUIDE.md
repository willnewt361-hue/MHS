# Mengo-Hub System - Complete Fix & Test Guide

## Quick Start (Recommended)

### On Windows - Run Complete Fix:
```batch
run_complete_fix.bat
```

This will:
1. Clean all Python cache files
2. Install/update all dependencies
3. Run comprehensive system checks
4. Start the server
5. Provide instructions for running interactive tests

---

## Individual Steps

### Step 1: Clean Python Cache
```batch
python -m py_compile .
REM Or manually:
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
```

### Step 2: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 3: Run Full System Check
```bash
python FULL_FIX_AND_TEST.py
```

This will verify:
- ✓ All required imports work
- ✓ Database connection
- ✓ Required tables exist
- ✓ Admin user exists
- ✓ Password hashing works
- ✓ Admin certificate created

### Step 4: Start the Server
```bash
python START_SYSTEM.py
```

Or run directly:
```bash
python run.py
```

### Step 5: Test Everything (In New Terminal)
```bash
python INTERACTIVE_TEST.py
```

This will test:
- ✓ Server connectivity
- ✓ Admin login (Newton / ##0000)
- ✓ CSV-imported user logins
- ✓ User lookup
- ✓ CSV import endpoint
- ✓ Admin endpoints
- ✓ Audit logs (A000 filtering)

---

## Test Credentials

### Admin (Super User):
- **Username**: Newton
- **Password**: ##0000
- **ID**: A000
- **Note**: Logins are NOT logged in audit logs

### CSV-Imported Students:
- **jdoe** / password123
- **asmith** / password123
- **bwilson** / password123

### CSV-Imported Teachers:
- **jane_smith** / password123
- **mike_jones** / password123
- **sarah_lee** / password123

---

## Troubleshooting

### Server Won't Start - ImportError
**Problem**: `ImportError: cannot import name 'create_app' from 'flask_app'`

**Solution**:
```bash
# Clean pycache completely
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc

# Then start again
python run.py
```

### Database Connection Failed
**Problem**: `ERROR: Failed to connect to postgresql`

**Solution**:
1. Check `.env` file - DATABASE_URL should be valid
2. Verify PostgreSQL is running
3. Or use SQLite by changing DATABASE_TYPE in .env to `sqlite`

### CSV Login Fails
**Problem**: Users imported from CSV cannot login

**Solution**:
1. Verify users were imported: `python FULL_FIX_AND_TEST.py`
2. Check database has correct password hashes
3. Run CSV import again via admin dashboard:
   - Go to `/admin/dashboard`
   - Use import password: `ImportPassword2026`

### Admin Certificate Issues
**Problem**: Admin redirected to certificate page repeatedly

**Solution**:
```bash
# Regenerate certificate
python FULL_FIX_AND_TEST.py

# Or from psql:
UPDATE super_admin_certificates SET is_active = 1 WHERE admin_id = 'A000';
```

### A000 Admin Logins in Audit Logs
**Problem**: A000 logins appearing in logs when they shouldn't

**Status**: ✓ FIXED - log_action() now filters A000 admin_login entries

---

## What Each Script Does

### START_SYSTEM.py
Master startup script that:
1. Checks requirements
2. Verifies .env file
3. Runs SETUP_AND_FIX.py
4. Mentions TEST_FEATURES.py
5. Starts the Flask server

### FULL_FIX_AND_TEST.py
Comprehensive diagnostic script that:
1. Cleans pycache
2. Verifies all imports
3. Tests database connection
4. Checks all required tables
5. Verifies admin user
6. Tests CSV-imported users
7. Tests password hashing
8. Creates admin certificate

### INTERACTIVE_TEST.py
HTTP-based testing that:
1. Tests server connectivity
2. Tests all login scenarios
3. Tests user lookup
4. Tests CSV import endpoint
5. Tests admin endpoints
6. Verifies audit logs

### run_complete_fix.bat
Windows batch script that runs everything automatically

---

## Key Fixes Applied

### 1. Fixed A000 Admin Logging
**File**: `flask_app.py` lines 541-544
- Added filter to skip logging A000 admin_login actions
- Regular users still logged normally

### 2. Fixed CSV User Logins
**File**: `flask_app.py` lines 636-658
- Removed is_admin requirement for regular user login
- CSV-imported users can now login

### 3. Fixed Admin Certificate System
**File**: `admin_service.py` lines 33-166
- Corrected table references (super_admin_certificates)
- Fixed field name (certificate_code)
- 10-year expiry implemented

### 4. Fixed Import Errors
**File**: `run.py` line 8
- Changed from factory pattern to direct import
- Now imports `app, socketio` correctly

**File**: `SETUP_AND_FIX.py` lines 10-11
- Added psycopg2.extras import with fallback

---

## System Status

✓ **COMPLETE** - All critical issues fixed:
- [x] A000 admin login filtering
- [x] CSV user login support
- [x] Admin certificate system
- [x] Audit logging
- [x] Import error handling
- [x] Comprehensive testing

---

## Next Steps

1. **Start the system**:
   ```bash
   run_complete_fix.bat
   ```

2. **In another terminal, test interactively**:
   ```bash
   python INTERACTIVE_TEST.py
   ```

3. **Access the dashboard**:
   - Admin: http://localhost:5000/admin/dashboard
   - User: http://localhost:5000

---

## Contact

For issues or questions about the Mengo-Hub system, review the test output and troubleshooting section above.
