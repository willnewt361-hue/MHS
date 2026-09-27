# Mengo-Hub Production System
A comprehensive educational platform built with Flask backend, featuring premium learning tools, real teacher chat, and secure admin controls.

## 🚀 Features
### Core Features
- **Secure Authentication**: bcrypt password hashing, login attempt lockout, admin override
- **Role-Based Access**: Students, Teachers, and Administrators with different permissions
- **Payment Integration**: Stripe payment processing for premium access
- **Real Teacher Chat**: Actual teachers receive notifications and reply to student messages
- **Admin Panel**: Certificate-based admin access with full system control

### Premium Features
- **Smart Revision**: AI-powered revision system based on UNEB patterns
- **Weakness Detector**: Analyzes student performance to identify weak areas
- **Exam Predictor**: Predicts exam questions based on patterns and performance
- **Binaural Beats**: Audio study aids for improved concentration
- **Interactive Quiz Sections**: Dynamic quizzes with explanations
- **3D Diagrams**: Interactive 3D visualizations for complex topics
- **Progress Analytics**: Detailed performance tracking and reporting
- **Personalized Study Plans**: AI-generated study schedules
- **Advanced AI Tools**: Integrated AI assistants for learning support
- **N8N Workflows**: Automated educational workflows
- **Summarizer**: AI-powered content summarization
- **Interactive Past Papers**: Dynamic past paper practice
- **Motivation Engine**: Gamified learning experience
- **Attendance Tracker**: Automated attendance monitoring
- **Report Generation**: Comprehensive academic reports

## 🛠️ Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite with parameterized queries
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Security**: bcrypt, JWT tokens, CORS, SSL/TLS
- **Deployment**: Nginx reverse proxy, Gunicorn WSGI server
- **Email**: SMTP notifications for teacher messages
- **File Storage**: Local file system with secure uploads

## 📋 Prerequisites
- Python 3.8+
- pip package manager
- Nginx web server
- SSL certificate (Let's Encrypt recommended)
- SMTP email service (Gmail, SendGrid, etc.)

## 🚀 Quick Start
### 1. Clone and Setup
```bash
git clone <repository-url>
cd mengo-hub-system
pip install -r requirements.txt
```

### Local Development
For local development on Windows, you do not need SSL or Gunicorn.
- Run the app directly with:
```powershell
python flask_app.py
```
- You can also use the included helper script:
```powershell
run_local.bat
```

> `ssl`, `gunicorn`, `nginx`, and `systemd` are only required for production deployment.
> Note: `chmod` and `sudo` are Linux/WSL commands.
> - On Windows use PowerShell or cmd for local setup.
> - For production, run the deployment script on a Linux server or WSL.
> - If you use Windows and Git Bash, `chmod +x deploy.sh` works there.

### 2. Environment Configuration
Create a `.env` file:
```env
SECRET_KEY=your-secret-key-here
ADMIN_ID=A000
ADMIN_SECRET_KEY=Newton
ADMIN_SECRET_PASSWORD=##0000
ADMIN_API_TOKEN=MengoAdminAPIToken2026
SUPER_ADMIN_API_TOKEN=MengoSuperAdminToken2026
ADMIN_IMPORT_PASSWORD=ImportPassword2026
LOGIN_ATTEMPTS_LIMIT=5
LOCKOUT_HOURS=24
DATABASE=data/mengo.db
FLASK_ENV=production
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Initialize Database
```bash
python populate_db.py
```

### 4. Run Development Server
```bash
python flask_app.py
```

### 5. Production Deployment
#### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 flask_app:app
```

#### Nginx Configuration
1. Copy `nginx.conf` to `/etc/nginx/sites-available/mengo-hub`
2. Update paths and domain in the configuration
3. Create symlink: `ln -s /etc/nginx/sites-available/mengo-hub /etc/nginx/sites-enabled/`
4. Test configuration: `nginx -t`
5. Reload nginx: `systemctl reload nginx`

#### SSL Setup (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📚 API Documentation
### Authentication
```
POST /api/login
Content-Type: application/json

{
  "username": "student_username",
  "password": "password123",
  "role": "student|teacher"
}
```

### Premium Features
#### Smart Revision
```
POST /api/premium/smart-revision
Content-Type: application/json

{
  "student_id": "S001",
  "subject": "Mathematics",
  "class": "S1"
}
```

#### Weakness Detector
```
GET /api/premium/weakness-detector?student_id=S001
```

#### Study Plan Generation
```
POST /api/premium/study-plan
Content-Type: application/json

{
  "student_id": "S001"
}
```

#### Quiz Generation
```
GET /api/premium/quiz?subject=Mathematics&difficulty=medium
```

### Teacher Chat
```
GET /api/messages?student_id=S001&teacher_id=T001
POST /api/messages
Content-Type: application/json

{
  "student_id": "S001",
  "teacher_id": "T001",
  "from_role": "student",
  "sender_id": "S001",
  "message": "Hello teacher!",
  "attachment_name": null
}
```

### Admin Endpoints
All admin endpoints require `Authorization: Bearer <ADMIN_API_TOKEN>` header.
```
GET /api/admin/users
GET /api/admin/admins
GET /api/admin/teachers
GET /api/admin/students
GET /api/admin/reports
POST /api/admin/upload-photo
GET /api/logs
POST /api/import-csv
```

### Super Admin Endpoints
All super admin endpoints require `Authorization: Bearer <SUPER_ADMIN_API_TOKEN>`.

```
GET /api/admin/super-reports
```

> Note: `A000` is reserved and not imported from CSV. Other admins may be added via CSV, but the super admin account remains hidden and trusted.
### CSV Import
The backend supports protected CSV import from `data/import.csv`.
- Use endpoint `POST /api/import-csv`
- Requires `Authorization: Bearer <ADMIN_API_TOKEN>`
- Requires the JSON body field `import_password`
- Default import password is set by `ADMIN_IMPORT_PASSWORD` in `.env`

Example:
```json
{
  "import_password": "ImportPassword2026",
  "csv_path": "data/import.csv"
}
```

## 🔒 Security Features
- **Password Security**: bcrypt hashing with salt
- **Login Protection**: Attempt limit with progressive lockout
- **Admin Override**: Special credentials for emergency access
- **Token Authentication**: JWT-based admin API access
- **Parameterized Queries**: SQL injection prevention
- **CORS Protection**: Configured for allowed origins
- **SSL/TLS**: HTTPS enforcement in production
- **Rate Limiting**: Nginx-based request throttling

## 🎯 User Roles
### Students
- Access to premium features (with payment)
- Teacher chat functionality
- Progress tracking and analytics
- Study plan access

### Teachers
- Receive student messages with email notifications
- Access to student performance data
- Participation in chat system

### Administrators
- Full system access via certificate authentication
- User management and monitoring
- System logs and analytics
- Photo upload management

## 📊 Database Schema
### Tables
- `students`: Student user accounts
- `teachers`: Teacher user accounts
- `messages`: Chat messages between students and teachers
- `payments`: Payment transaction records
- `loginLogs`: Authentication attempt logs
- `quiz_questions`: Premium quiz content
- `student_performance`: Performance analytics data
- `study_plans`: AI-generated study plans

## 🔧 Configuration
### Environment Variables
- `SECRET_KEY`: Flask session secret
- `ADMIN_SECRET_KEY`: Admin override username
- `ADMIN_SECRET_PASSWORD`: Admin override password
- `ADMIN_API_TOKEN`: API token for admin endpoints
- `LOGIN_ATTEMPTS_LIMIT`: Max login attempts before lockout
- `LOCKOUT_HOURS`: Lockout duration in hours
- `DATABASE`: SQLite database path

### Nginx Tuning
- Rate limiting zones for API protection
- SSL/TLS configuration
- Static file caching
- Proxy buffer settings

## 📈 Monitoring
### Logs
- Application logs: Flask app stdout/stderr
- Access logs: Nginx access logs
- Error logs: Nginx error logs
- Database logs: SQLite query logs

### Health Checks
- `/api/health` endpoint for system status
- Database connection monitoring
- Memory and CPU usage tracking

## 🚨 Troubleshooting
### Common Issues
1. **Database Connection Errors**
   - Ensure `data/` directory exists and is writable
   - Check SQLite file permissions

2. **Email Notifications Not Working**
   - Verify SMTP credentials in `.env`
   - Check firewall settings for SMTP port

3. **Admin Access Denied**
   - Verify `ADMIN_API_TOKEN` in request headers
   - Check token format: `Bearer <token>`

4. **File Upload Failures**
   - Ensure upload directories exist and are writable
   - Check file size limits in Nginx config
## 📖 Code Documentation

This section provides detailed line-by-line documentation for every file in the Mengo-Hub system.

### flask_app.py (Main Server Application)
**Lines 1-20: Imports and Setup**
- `from flask import Flask, request, jsonify, send_file, send_from_directory, session, g`: Import Flask web framework components for routing, responses, sessions, and global context
- `import sqlite3, psycopg2, psycopg2.extras`: Database drivers for SQLite and PostgreSQL support
- `import bcrypt`: Password hashing library for secure authentication
- `import os, json, csv, base64`: Standard libraries for file operations, data parsing, and encoding
- `import smtplib, email.mime.text`: Email functionality for teacher notifications
- `import datetime, timedelta, secrets, re`: Date/time handling, secure token generation, regex validation
- `from werkzeug.utils import secure_filename`: File upload security
- `from flask_cors import CORS`: Cross-origin resource sharing support
- `from dotenv import load_dotenv`: Environment variable loading
- `import random, uuid, pathlib`: Randomization, unique ID generation, path handling

**Lines 21-40: Flask Application Initialization**
- `load_dotenv()`: Load environment variables from .env file
- `app = Flask(__name__, static_folder='public', static_url_path='')`: Create Flask app with public directory as static files
- `CORS(app)`: Enable CORS for API access
- `app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))`: Set session secret key with fallback

**Lines 41-60: Configuration Variables**
- `ADMIN_ID, ADMIN_SECRET_KEY, etc.`: Define admin credentials and API tokens from environment
- `LOGIN_ATTEMPTS_LIMIT, LOCKOUT_HOURS`: Security settings for login protection
- `DATABASE_TYPE, DATABASE_URL`: Database configuration
- `IMPORT_CSV_PATH, UPLOAD_FOLDER`: File paths for data import and uploads
- `ALLOWED_EXTENSIONS`: Permitted file types for uploads

**Lines 61-80: Directory Creation**
- `os.makedirs()` calls: Ensure required directories exist for data storage and uploads

**Lines 81-100: DatabaseWrapper Class**
- Class for handling database connections and queries
- Supports both SQLite and PostgreSQL
- Provides connection management and query execution methods

**Lines 101-120: Database Connection Functions**
- `get_db()`: Get database connection for current request
- `close_db()`: Close database connection after request
- `init_db()`: Initialize database with schema
- `get_db_connection()`: Create new database connection

**Lines 121-140: Authentication Functions**
- `hash_password()`: Hash passwords using bcrypt
- `verify_password()`: Verify passwords against hashes
- `generate_session_token()`: Create secure session tokens
- `validate_session()`: Check session validity

**Lines 141-160: Login Attempt Protection**
- `check_login_attempts()`: Track failed login attempts
- `reset_login_attempts()`: Clear attempt counter on success
- `is_account_locked()`: Check if account is temporarily locked

**Lines 161-180: User Management Functions**
- `get_user_by_username()`: Retrieve user data by username
- `update_user_login_time()`: Update last login timestamp
- `log_login_attempt()`: Record login attempts for security

**Lines 181-200: API Route Definitions**
- `@app.route('/')`: Serve main application page
- `@app.route('/api/login', methods=['POST'])`: Handle user authentication
- Various other route decorators for different endpoints

**Lines 201-220: Login Endpoint Implementation**
- Parse JSON request data
- Validate credentials
- Check account status and login attempts
- Generate session token on success
- Return appropriate error messages

**Lines 221-240: Payment Processing**
- `@app.route('/api/pay', methods=['POST'])`: Handle payment requests
- Validate user session and payment data
- Process Airtel Money payments
- Update user payment status
- Generate certificates for paid users

**Lines 241-260: Certificate Generation**
- Create JSON certificates for different user types
- Set appropriate permissions and expiry dates
- Store certificate data in database

**Lines 261-280: Admin Endpoints**
- `@app.route('/api/admin/users')`: Get all users
- `@app.route('/api/admin/admins')`: Get admin users
- Authentication checks for admin access
- Database queries for user data

**Lines 281-300: Teacher and Student Management**
- `@app.route('/api/admin/teachers')`: Manage teacher accounts
- `@app.route('/api/admin/students')`: Manage student accounts
- CRUD operations for user management

**Lines 301-320: Message System**
- `@app.route('/api/messages', methods=['GET', 'POST'])`: Handle chat messages
- Store messages in database
- Send email notifications to teachers
- Support file attachments

**Lines 321-340: File Upload Handling**
- `@app.route('/api/upload', methods=['POST'])`: Handle file uploads
- Validate file types and sizes
- Store files securely
- Update database with file references

**Lines 341-360: Timetable and Notes**
- `@app.route('/api/timetable/<stream>')`: Serve timetable data
- `@app.route('/api/notes/<subject>/<note>')`: Serve subject notes
- Load JSON and text files from filesystem

**Lines 361-380: Feedback System**
- `@app.route('/api/feedback', methods=['POST'])`: Handle user feedback
- Store feedback in database
- Optional email notifications

**Lines 381-400: Logging and Monitoring**
- `@app.route('/api/logs')`: Serve application logs
- `@app.route('/api/health')`: Health check endpoint
- System status monitoring

**Lines 401-420: CSV Import**
- `@app.route('/api/import-csv', methods=['POST'])`: Import users from CSV
- Validate admin access
- Parse CSV data
- Create user accounts with hashed passwords

**Lines 421-440: Static File Serving**
- `@app.route('/<path:path>')`: Serve static files
- Handle different file types
- Security checks for file access

**Lines 441-460: Application Startup**
- `if __name__ == '__main__':`: Main execution block
- `init_db()`: Initialize database
- `app.run()`: Start Flask development server

### public/index.html (Home Page)

**Lines 1-10: HTML Structure**
- Standard HTML5 document declaration
- Meta tags for character encoding and viewport
- Page title and CSS stylesheet link

**Lines 11-30: Hero Section**
- Main landing page container
- Logo and branding elements
- Welcome message and call-to-action buttons

**Lines 31-50: Features Display**
- Feature cards showing platform capabilities
- Icons and descriptions for each feature
- Responsive grid layout

**Lines 51-70: Role Selection Modal**
- Modal dialog for user role selection
- Student and teacher options
- JavaScript event handlers

**Lines 71-90: Certificate Check Script**
- IndexedDB setup for certificate storage
- Access certificate validation
- Modal display logic based on certificate status

### public/login.html (Login Page)

**Lines 1-20: Page Structure**
- HTML head with title and styles
- Login form container
- Radio buttons for role selection

**Lines 21-40: Form Elements**
- Username and password input fields
- Role selection radio buttons
- Submit button and links

**Lines 41-60: JavaScript Logic**
- Form validation
- API calls for authentication
- Session management
- Error handling

### public/dashboard.html (Main Dashboard)

**Lines 1-30: Dashboard Layout**
- Navigation sidebar
- Main content area
- User info display

**Lines 31-50: Feature Sections**
- Updates/announcements area
- Quick access buttons
- User-specific content

**Lines 51-70: Bible Quotes Display**
- Daily quote rotation
- 2-day display cycle
- Inspirational content

**Lines 71-90: Role-Based Features**
- Conditional display based on user role
- Teacher/student specific sections
- Assignment and timetable access

### public/admin.html (Admin Panel)

**Lines 1-40: Admin Interface**
- Certificate-based access control
- User management sections
- System monitoring tools

**Lines 41-60: User Lists**
- Student and teacher tables
- Account status indicators
- Action buttons for management

**Lines 61-80: System Controls**
- Import/export functions
- Log viewing
- Configuration options

### public/teacher-chat.html (Teacher Consultation)

**Lines 1-30: Chat Interface**
- Message display area
- Input form for new messages
- File attachment support

**Lines 31-50: Message History**
- Load previous conversations
- Display sender information
- Timestamp formatting

**Lines 51-70: Real-time Updates**
- Periodic message checking
- Notification system
- Auto-scroll functionality

### public/subject-detail.html (Subject Notes)

**Lines 1-20: Subject Layout**
- Subject title and navigation
- Notes sidebar
- Content display area

**Lines 21-40: Notes Loading**
- Fetch subject notes from server
- Display subtopics
- Content rendering

**Lines 41-60: Interactive Features**
- Expandable sections
- Search functionality
- Download options

### public/feedback.html (Feedback Form)

**Lines 1-15: Form Structure**
- Feedback input fields
- Rating system
- Submit button

**Lines 16-30: Validation and Submission**
- Form validation
- API call to submit feedback
- Success/error messages

### data/schema.sql (Database Schema)

**Lines 1-20: Table Creation**
- CREATE TABLE statements for all tables
- Column definitions with data types
- Primary key and foreign key constraints

**Lines 21-40: Index Creation**
- Performance indexes on frequently queried columns
- Unique constraints for data integrity

**Lines 41-60: Initial Data**
- INSERT statements for default data
- Admin user creation
- System configuration data

### requirements.txt (Python Dependencies)

**Lines 1-10: Core Dependencies**
- Flask web framework
- Database drivers (sqlite3, psycopg2)
- Security libraries (bcrypt, python-dotenv)
- Email support (smtplib)

**Lines 11-20: Additional Libraries**
- File handling (werkzeug)
- CORS support (flask-cors)
- Date/time utilities

### nginx.conf (Web Server Configuration)

**Lines 1-20: Server Block**
- Listen directives for HTTP/HTTPS
- Server name configuration
- SSL certificate paths

**Lines 21-40: Location Blocks**
- Static file serving
- API proxy configuration
- Security headers

**Lines 41-60: Rate Limiting**
- Request limiting zones
- DDoS protection rules
- Performance optimizations

### deploy.sh (Deployment Script)

**Lines 1-20: Environment Setup**
- Update system packages
- Install Python and pip
- Create application directory

**Lines 21-40: Application Deployment**
- Clone repository
- Install dependencies
- Configure environment variables

**Lines 41-60: Service Configuration**
- Setup systemd service
- Configure nginx
- SSL certificate installation

### mengo-hub.service (Systemd Service)

**Lines 1-10: Service Definition**
- Service name and description
- User and group configuration
- Working directory

**Lines 11-20: Execution Parameters**
- ExecStart command
- Environment variables
- Restart policy

### run_local.bat (Windows Development)

**Lines 1-10: Environment Setup**
- Activate virtual environment
- Set environment variables
- Start Flask application

### populate_db.py (Database Population)

**Lines 1-20: Data Generation**
- Sample user creation
- Test data insertion
- Performance testing data

**Lines 21-40: Batch Operations**
- Bulk data import
- Relationship creation
- Data validation

### .env.example (Environment Template)

**Lines 1-20: Configuration Variables**
- Database settings
- Security keys
- API tokens
- Email configuration

### POSTGRESQL_SETUP.md (Database Setup)

**Lines 1-30: PostgreSQL Installation**
- Installation instructions
- User creation
- Database setup

**Lines 31-50: Migration Steps**
- Schema creation
- Data migration from SQLite
- Performance optimization

### PREMIUM_FEATURES.md (Premium Features)

**Lines 1-40: Feature Descriptions**
- AI-powered learning tools
- Advanced analytics
- Interactive content

**Lines 41-60: Implementation Details**
- API endpoints
- Database schemas
- Frontend integration

### data/timetables/*.json (Timetable Data)

**JSON Structure:**
- Stream-specific schedules
- Time slots and subjects
- Teacher assignments

### data/notes/*/*.txt (Subject Notes)

**Content Structure:**
- Topic-based organization
- Plain text notes
- Reference materials

### public/audio/beats/ (Audio Files)

**File Organization:**
- Binaural beat audio files
- Study aid tracks
- Concentration enhancement

### public/images/students/ (Student Photos)

**Naming Convention:**
- student_id.jpg/png
- Secure upload handling
- Privacy protection

### public/images/teachers/ (Teacher Photos)

**Naming Convention:**
- teacher_id.jpg/png
- Profile picture storage
- Access control

### public/style.css (Global Styles)

**Lines 1-50: Base Styles**
- CSS reset and typography
- Color scheme and variables
- Layout utilities

**Lines 51-100: Component Styles**
- Button and form styling
- Modal and overlay styles
- Responsive design rules

**Lines 101-150: Page-Specific Styles**
- Dashboard layout
- Chat interface styling
- Admin panel design

### public/auth.js (Authentication Logic)

**Lines 1-30: Login Handling**
- Form submission
- API communication
- Session management

**Lines 31-50: Error Handling**
- Validation messages
- Network error recovery
- User feedback

### public/dashboard.js (Dashboard Functionality)

**Lines 1-50: Initialization**
- User data loading
- UI setup
- Event binding

**Lines 51-100: Feature Loading**
- Timetable display
- Assignment management
- Message system integration

**Lines 101-150: Role-Based Logic**
- Permission checking
- Content filtering
- Admin function access

### public/admin.js (Admin Panel Logic)

**Lines 1-50: User Management**
- User list loading
- CRUD operations
- Status updates

**Lines 51-100: System Monitoring**
- Log viewing
- Statistics display
- Configuration management

### public/teacher-chat.js (Chat System)

**Lines 1-30: Message Loading**
- Conversation history
- Real-time updates
- File attachment handling

**Lines 31-50: Message Sending**
- Form validation
- API submission
- UI updates

### public/subject-detail.js (Notes Display)

**Lines 1-20: Subject Loading**
- API calls for notes
- Content rendering
- Navigation setup

**Lines 21-40: Interactive Features**
- Expandable sections
- Search functionality
- Download handling

### public/feedback.js (Feedback System)

**Lines 1-15: Form Handling**
- Input validation
- Submission logic
- Response handling

### public/payment.js (Payment Processing)

**Lines 1-30: Payment Initiation**
- User validation
- Payment form setup
- API integration

**Lines 31-50: Status Checking**
- Transaction verification
- Certificate generation
- UI updates

### public/install.js (Certificate Installation)

**Lines 1-30: IndexedDB Setup**
- Database initialization
- Certificate storage
- Retrieval functions

**Lines 31-50: Certificate Generation**
- Form processing
- JSON creation
- Display and installation

### public/admin-installer.js (Admin Certificate Management)

**Lines 1-50: Certificate Creation**
- Admin form handling
- Certificate generation
- Permission setting

**Lines 51-100: Installation Logic**
- Browser storage
- Validation checks
- Error handling

### .gitignore (Git Ignore Rules)

**Lines 1-20: Ignored Files**
- Environment files
- Database files
- Log files
- Temporary files

### txt.txt (Miscellaneous Notes)

**Content:**
- Development notes
- TODO items
- Configuration reminders
## 📝 Development
### Adding New Features
1. Create database migrations if needed
2. Add routes to `flask_app.py`
3. Update frontend JavaScript files
4. Test with sample data
5. Update documentation

### Testing
```bash
# Run with test database
DATABASE=data/test.db python flask_app.py

# Populate test data
python populate_db.py
```

## 📄 License
This project is licensed under the terms specified in LICENSE.txt.

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support
For support and questions:
- Email: support@mengo-hub.com
- Documentation: [Full API Docs](api-docs.md)
- Issues: GitHub Issues

---
**Built with ❤️ for Ugandan students and teachers**