# System Requirements
## Blood Donation Network - Technical Specifications

---

## 📋 Table of Contents
1. [Hardware Requirements](#1-hardware-requirements)
2. [Software Requirements](#2-software-requirements)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [System Architecture](#5-system-architecture)
6. [Development Requirements](#6-development-requirements)
7. [Deployment Requirements](#7-deployment-requirements)

---

## 💻 1. Hardware Requirements

### 1.1 Development Environment

#### Minimum Requirements:
- **Processor**: Intel Core i3 / AMD Ryzen 3 or equivalent
- **RAM**: 4 GB
- **Storage**: 1 GB available space
- **Internet**: Broadband connection (1 Mbps)
- **Display**: 1366x768 resolution

#### Recommended Requirements:
- **Processor**: Intel Core i5 / AMD Ryzen 5 or higher
- **RAM**: 8 GB or more
- **Storage**: 5 GB SSD available space
- **Internet**: High-speed broadband (10 Mbps+)
- **Display**: 1920x1080 resolution or higher

### 1.2 Production Server

#### Minimum Requirements:
- **Processor**: 1 vCPU / 2 GHz
- **RAM**: 512 MB
- **Storage**: 2 GB SSD
- **Bandwidth**: 100 GB/month
- **Uptime**: 99% availability

#### Recommended Requirements:
- **Processor**: 2+ vCPU / 2.5 GHz
- **RAM**: 1-2 GB
- **Storage**: 10 GB SSD
- **Bandwidth**: Unmetered
- **Uptime**: 99.9% availability

### 1.3 Client (End User) Requirements

#### Desktop/Laptop:
- **Processor**: Any modern processor (1 GHz+)
- **RAM**: 2 GB minimum
- **Internet**: 512 Kbps minimum
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

#### Mobile Devices:
- **RAM**: 1 GB minimum
- **Internet**: 3G/4G/5G or WiFi
- **Browser**: Mobile browser with HTML5 support
- **Screen**: Any size (responsive design)

---

## 🛠️ 2. Software Requirements

### 2.1 Development Environment

#### Required Software:
| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.7+ (Recommended: 3.11+) | Backend programming language |
| **pip** | Latest | Python package manager |
| **Git** | 2.0+ | Version control |
| **Text Editor/IDE** | Any | Code editing (VS Code, PyCharm, Sublime) |
| **Web Browser** | Latest | Testing (Chrome DevTools recommended) |

#### Python Dependencies:
```txt
Flask==3.0.0
Werkzeug==3.0.1
reportlab==4.0.7
Pillow==10.1.0
Flask-Mail==0.9.1
```

### 2.2 Production Server

#### Required Software:
- **Operating System**: 
  - Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
  - Windows Server 2019+
  - macOS 11+ (for small deployments)

- **Python Runtime**: Python 3.7+ with pip

- **Web Server** (Choose one):
  - Gunicorn (recommended for Linux)
  - uWSGI
  - Waitress (for Windows)
  - Apache with mod_wsgi
  - Nginx with reverse proxy

- **Database**:
  - SQLite 3.x (included with Python, suitable for < 100 concurrent users)
  - PostgreSQL 12+ (recommended for production)
  - MySQL 8.0+ (alternative)

- **Optional**:
  - Redis (for session management and caching)
  - SSL/TLS Certificate (Let's Encrypt for HTTPS)

### 2.3 Client Requirements

#### Supported Browsers:
- **Google Chrome**: Version 90+
- **Mozilla Firefox**: Version 88+
- **Safari**: Version 14+
- **Microsoft Edge**: Version 90+
- **Opera**: Version 75+

#### Browser Features Required:
- JavaScript enabled
- Cookies enabled
- HTML5 support
- CSS3 support
- LocalStorage support

---

## ⚙️ 3. Functional Requirements

### 3.1 User Management

#### FR-1: User Registration
- **Description**: Users can register as Donor or Receiver
- **Input**: Name, Email, Phone, Address, Password, Role, Blood Group (for donors)
- **Process**: Validate data, hash password, store in database
- **Output**: User account created, redirect to login
- **Validation**: Email uniqueness, phone format, password strength (6+ chars)

#### FR-2: User Authentication
- **Description**: Secure login system for users and admin
- **Input**: Email and password
- **Process**: Verify credentials, create session
- **Output**: Access to role-based dashboard
- **Security**: Password hashing (SHA-256), session management

#### FR-3: Profile Management
- **Description**: Users can view and edit profile information
- **Input**: Updated user details, profile picture
- **Process**: Validate changes, update database
- **Output**: Updated profile, confirmation message
- **Features**: Profile picture upload (max 5MB, JPG/PNG/GIF)

#### FR-4: Password Reset
- **Description**: Forgot password functionality
- **Input**: Email address, new password
- **Process**: Generate token, validate token, update password
- **Output**: Password reset confirmation
- **Security**: Token expiry (1 hour), one-time use

### 3.2 Donor Features

#### FR-5: Donor Dashboard
- **Description**: View donor-specific information and actions
- **Display**: Blood group, availability status, donation count
- **Actions**: Update availability, view donation history, search receivers
- **Statistics**: Total donations, lives saved, next eligible date

#### FR-6: Availability Management
- **Description**: Toggle availability status
- **Input**: Available/Unavailable selection
- **Process**: Update donor_details table
- **Output**: Status confirmation, updated dashboard

#### FR-7: Donation History
- **Description**: Track all blood donations with certificates
- **Display**: Date, blood group, units, center, certificate
- **Actions**: Add donation, download PDF certificate
- **Calculations**: Lives saved (×3), next eligible date (+90 days)
- **Badges**: Hero (1+), Bronze (5+), Silver (10+), Gold (25+), Platinum (50+)

### 3.3 Receiver Features

#### FR-8: Donor Search
- **Description**: Search available donors by blood group
- **Input**: Blood group selection
- **Process**: Query database for available donors
- **Output**: List of matching donors with contact info
- **Display**: Compatibility guide, donor details

#### FR-9: Blood Request System
- **Description**: Create urgent blood requests
- **Input**: Blood group, units, urgency, hospital, contact, notes
- **Process**: Validate data, store request
- **Output**: Active request posted, visible to all users
- **Urgency Levels**: Normal, Urgent, Critical (color-coded)

#### FR-10: View Blood Requests
- **Description**: Display all active blood requests
- **Sorting**: Priority-based (Critical → Urgent → Normal)
- **Display**: Request details, urgency badge, contact buttons
- **Actions**: Call donor, email donor

### 3.4 Admin Features

#### FR-11: Admin Dashboard
- **Description**: Comprehensive admin panel with analytics
- **Statistics**: Total users, donors, receivers, donations, requests
- **Charts**: Blood group distribution (Chart.js doughnut chart)
- **Actions**: Search users, manage accounts, export data

#### FR-12: User Management
- **Description**: Admin can manage all user accounts
- **Actions**: 
  - Search by name/email/blood group
  - Block/unblock users
  - Delete users permanently
  - View user details
- **Display**: Sortable user table with all information

#### FR-13: Data Export
- **Description**: Export user data to CSV
- **Output**: CSV file with all user information
- **Filename**: users_export_YYYYMMDD_HHMMSS.csv
- **Fields**: ID, Name, Email, Phone, Role, Blood Group, Status, etc.

### 3.5 Health & Wellness Features

#### FR-14: Health Eligibility Checker
- **Description**: BMI-based eligibility assessment
- **Input**: Age, weight (kg), height (cm)
- **Process**: Calculate BMI, validate criteria
- **Output**: Eligibility status with explanation
- **Criteria**: Age 18-65, Weight ≥50kg, BMI 18.5-35

#### FR-15: Diet Plan for Donors
- **Description**: Nutritional guide for blood donors
- **Content**: Before, during, after donation meal plans
- **Sections**: Food recommendations, sample menus, nutrients
- **Format**: Organized HTML page with sections

### 3.6 Live Statistics

#### FR-16: Real-time Dashboard
- **Description**: Auto-refreshing statistics page
- **Refresh**: Every 30 seconds
- **Display**: Live counts, blood group distribution, recent requests
- **API**: JSON endpoints for data fetching

---

## 🎯 4. Non-Functional Requirements

### 4.1 Performance Requirements

#### NFR-1: Response Time
- **Page Load**: < 2 seconds for standard pages
- **Database Queries**: < 500ms for simple queries
- **Search Results**: < 1 second for donor search
- **API Responses**: < 200ms for statistics

#### NFR-2: Scalability
- **Concurrent Users**: Support 100-500 concurrent users (SQLite)
- **Database Growth**: Handle 10,000+ user records
- **Request Volume**: 1000+ requests/day
- **Future**: Upgradable to PostgreSQL for larger scale

#### NFR-3: Throughput
- **User Registration**: 50 registrations/hour
- **Blood Requests**: 100 requests/day
- **Donor Searches**: 500 searches/hour
- **Admin Operations**: 200 operations/hour

### 4.2 Security Requirements

#### NFR-4: Authentication & Authorization
- **Password Hashing**: Werkzeug PBKDF2 SHA-256
- **Session Management**: Secure server-side sessions
- **Role-based Access**: Decorator-based route protection
- **Token Security**: Cryptographically secure random tokens

#### NFR-5: Data Protection
- **SQL Injection**: Parameterized queries
- **XSS Prevention**: Input sanitization, output encoding
- **CSRF Protection**: Flask built-in CSRF tokens
- **File Upload**: Type validation, size limits, secure filenames

#### NFR-6: Privacy
- **Data Encryption**: HTTPS in production (TLS 1.2+)
- **Sensitive Data**: Passwords hashed, never stored plain
- **User Consent**: Clear privacy policy
- **Data Retention**: User-controlled profile deletion

### 4.3 Reliability Requirements

#### NFR-7: Availability
- **Uptime**: 99% minimum (8.76 hours downtime/year)
- **Target**: 99.9% (52.56 minutes downtime/year)
- **Maintenance Window**: Scheduled off-peak hours

#### NFR-8: Error Handling
- **User Errors**: Friendly error messages, no technical details
- **Server Errors**: Logged with timestamps, graceful degradation
- **Database Errors**: Transaction rollback, data integrity maintained
- **Validation**: Client-side and server-side validation

#### NFR-9: Backup & Recovery
- **Database Backup**: Daily automated backups
- **Retention**: 30-day backup history
- **Recovery Time**: < 4 hours
- **Recovery Point**: < 24 hours of data loss

### 4.4 Usability Requirements

#### NFR-10: User Interface
- **Design**: Modern, professional, medical theme
- **Consistency**: Uniform navigation across all pages
- **Accessibility**: WCAG 2.1 Level AA compliance target
- **Feedback**: Clear success/error messages

#### NFR-11: Responsive Design
- **Mobile**: Fully functional on smartphones (320px+)
- **Tablet**: Optimized for tablets (768px+)
- **Desktop**: Enhanced experience (1024px+)
- **Framework**: Bootstrap 5 responsive grid

#### NFR-12: Learnability
- **New Users**: < 10 minutes to register and search
- **Documentation**: Complete README and user guides
- **Help**: Tooltips and inline help text
- **Navigation**: < 3 clicks to any feature

### 4.5 Maintainability Requirements

#### NFR-13: Code Quality
- **Structure**: MVC-style organization
- **Documentation**: Inline comments for complex logic
- **Standards**: PEP 8 Python style guide
- **Modularity**: Reusable functions and components

#### NFR-14: Database Design
- **Normalization**: Third Normal Form (3NF)
- **Indexing**: Primary keys, foreign keys indexed
- **Constraints**: Data integrity enforced
- **Schema**: Clear table relationships

#### NFR-15: Version Control
- **System**: Git with semantic versioning
- **Branching**: Feature branches, main/production
- **Commits**: Clear, descriptive commit messages
- **Documentation**: CHANGELOG maintained

### 4.6 Compatibility Requirements

#### NFR-16: Browser Compatibility
- **Cross-browser**: Works on all major browsers
- **Graceful Degradation**: Basic functionality without JavaScript
- **Progressive Enhancement**: Enhanced features for modern browsers

#### NFR-17: Platform Independence
- **Operating System**: Windows, Linux, macOS
- **Python**: Version 3.7 to 3.12+
- **Database**: SQLite, PostgreSQL, MySQL compatible

---

## 🏗️ 5. System Architecture

### 5.1 Architecture Pattern
- **Type**: Model-View-Controller (MVC)
- **Framework**: Flask (micro-framework)
- **Database**: Relational (SQLite/PostgreSQL)
- **API**: RESTful endpoints

### 5.2 System Components

#### Frontend Layer:
- **Templates**: Jinja2 template engine
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js 4.4.0
- **JavaScript**: Vanilla JS (no jQuery dependency)

#### Backend Layer:
- **Web Framework**: Flask 3.0.0
- **Security**: Werkzeug security utilities
- **PDF Generation**: ReportLab 4.0.7
- **Image Processing**: Pillow 10.1.0
- **Email** (ready): Flask-Mail 0.9.1

#### Data Layer:
- **Database**: SQLite 3.x (development)
- **ORM Alternative**: Raw SQL with parameterized queries
- **Schema**: 4 tables (users, donor_details, donations, blood_requests, password_reset_tokens)

### 5.3 Database Schema

#### Table: users
```sql
- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL)
- email (TEXT UNIQUE NOT NULL)
- phone (TEXT)
- address (TEXT)
- role (TEXT NOT NULL) -- 'donor', 'receiver', 'admin'
- password_hash (TEXT NOT NULL)
- status (TEXT DEFAULT 'active') -- 'active', 'blocked'
- profile_picture (TEXT)
- last_login (TIMESTAMP)
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

#### Table: donor_details
```sql
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER FOREIGN KEY)
- blood_group (TEXT NOT NULL) -- 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
- availability_status (TEXT DEFAULT 'available')
- last_donation_date (DATE)
- total_donations (INTEGER DEFAULT 0)
```

#### Table: donations
```sql
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER FOREIGN KEY)
- donation_date (DATE NOT NULL)
- blood_group (TEXT NOT NULL)
- units_donated (REAL DEFAULT 1)
- donation_center (TEXT)
- certificate_number (TEXT UNIQUE)
- next_eligible_date (DATE)
- notes (TEXT)
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

#### Table: blood_requests
```sql
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER FOREIGN KEY)
- blood_group (TEXT NOT NULL)
- units_needed (INTEGER NOT NULL)
- urgency (TEXT NOT NULL) -- 'normal', 'urgent', 'critical'
- hospital_name (TEXT NOT NULL)
- contact_person (TEXT NOT NULL)
- contact_phone (TEXT NOT NULL)
- notes (TEXT)
- status (TEXT DEFAULT 'active')
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

#### Table: password_reset_tokens
```sql
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER FOREIGN KEY)
- token (TEXT UNIQUE NOT NULL)
- expires_at (TIMESTAMP NOT NULL)
- used (INTEGER DEFAULT 0)
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

### 5.4 System Flow Diagrams

#### User Registration Flow:
```
User → Registration Form → Validation → Password Hashing 
  → Database Insert → Email Confirmation (optional) → Login Page
```

#### Blood Request Flow:
```
Receiver → Create Request Form → Validation → Database Insert 
  → Display in Active Requests → Donors View → Contact Receiver
```

#### Donation Recording Flow:
```
Donor → Add Donation Form → Validation → Database Insert 
  → Generate Certificate → Update Statistics → Download PDF
```

---

## 👨‍💻 6. Development Requirements

### 6.1 Development Environment Setup

#### Step 1: Install Python
```powershell
# Windows
Download from python.org (3.11+ recommended)

# Linux
sudo apt update
sudo apt install python3 python3-pip

# macOS
brew install python@3.11
```

#### Step 2: Clone/Setup Project
```powershell
cd blood_donation_network
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac
```

#### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Step 4: Initialize Database
```powershell
python app.py  # Auto-creates blood_donation.db
```

### 6.2 Development Tools

#### Recommended IDE:
- **Visual Studio Code**: Free, excellent Python support
  - Extensions: Python, Pylance, Flask Snippets
- **PyCharm**: Professional Python IDE
- **Sublime Text**: Lightweight alternative

#### Version Control:
- **Git**: For source control
- **GitHub/GitLab**: Remote repository hosting

#### Testing Tools:
- **Browser DevTools**: Chrome/Firefox developer tools
- **Postman**: API testing
- **pytest**: Unit testing (optional)

### 6.3 Coding Standards

#### Python (PEP 8):
- Indentation: 4 spaces
- Line length: 79 characters (max 99)
- Naming: snake_case for functions/variables
- Docstrings: For all functions

#### HTML/CSS:
- Indentation: 2 spaces
- BEM methodology for CSS classes
- Semantic HTML5 elements
- Accessibility attributes (aria-*)

#### JavaScript:
- ES6+ features
- Camel case for variables
- Meaningful function names
- Comments for complex logic

---

## 🚀 7. Deployment Requirements

### 7.1 Deployment Options

#### Option 1: PythonAnywhere (Free Tier)
- **Cost**: Free
- **Setup**: Upload files, configure WSGI
- **Database**: SQLite (included)
- **HTTPS**: Included
- **Limitations**: 512MB storage, custom domain (paid)

#### Option 2: Heroku (Free/Hobby)
- **Cost**: Free tier available
- **Setup**: Git push deployment
- **Database**: PostgreSQL addon
- **HTTPS**: Included
- **CLI**: Heroku CLI required

#### Option 3: AWS EC2
- **Cost**: Free tier (12 months), then ~$5-10/month
- **Setup**: Ubuntu server + Nginx + Gunicorn
- **Database**: RDS or local PostgreSQL
- **HTTPS**: Let's Encrypt (free)
- **Scalability**: High

#### Option 4: DigitalOcean Droplet
- **Cost**: $5/month minimum
- **Setup**: Ubuntu + Nginx + Gunicorn
- **Database**: PostgreSQL on same server
- **HTTPS**: Let's Encrypt
- **Performance**: Good

#### Option 5: Shared Hosting (cPanel)
- **Cost**: $3-10/month
- **Setup**: Upload files, Python app setup
- **Database**: MySQL/PostgreSQL
- **HTTPS**: Often included
- **Control**: Limited

### 7.2 Production Configuration

#### Environment Variables:
```python
SECRET_KEY = 'your-production-secret-key'
DATABASE_URL = 'postgresql://user:pass@host/db'
FLASK_ENV = 'production'
DEBUG = False
```

#### Web Server (Gunicorn):
```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 app:app
```

#### Nginx Configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### SSL/TLS (Let's Encrypt):
```bash
sudo certbot --nginx -d yourdomain.com
```

### 7.3 Database Migration (SQLite → PostgreSQL)

#### For Production:
```python
# Install psycopg2
pip install psycopg2-binary

# Update app.py
import psycopg2
DATABASE = os.environ.get('DATABASE_URL')

# Export from SQLite
sqlite3 blood_donation.db .dump > backup.sql

# Import to PostgreSQL
psql -U user -d database < backup.sql
```

### 7.4 Performance Optimization

#### Production Checklist:
- ✅ Enable HTTPS (SSL/TLS)
- ✅ Set DEBUG = False
- ✅ Use production WSGI server (Gunicorn/uWSGI)
- ✅ Configure proper secret key
- ✅ Enable gzip compression
- ✅ Set up CDN for static files (optional)
- ✅ Configure database connection pooling
- ✅ Implement caching (Redis)
- ✅ Set up monitoring (Sentry, New Relic)
- ✅ Regular backups automated

### 7.5 Security Hardening

#### Production Security:
- 🔒 HTTPS only (redirect HTTP to HTTPS)
- 🔒 Security headers (CSP, X-Frame-Options)
- 🔒 Rate limiting on login endpoints
- 🔒 Regular security updates
- 🔒 Firewall configuration
- 🔒 Disable directory listing
- 🔒 Hide server version headers
- 🔒 Input validation and sanitization
- 🔒 Regular backup verification

---

## 📊 8. Testing Requirements

### 8.1 Testing Types

#### Unit Testing:
- Test individual functions
- Validate data processing
- Check calculations (BMI, lives saved, etc.)

#### Integration Testing:
- Test database operations
- Validate form submissions
- Check route protection

#### User Acceptance Testing:
- Test complete user workflows
- Verify all features work end-to-end
- Cross-browser testing

#### Security Testing:
- SQL injection attempts
- XSS vulnerability checks
- Authentication bypass attempts
- File upload security

### 8.2 Test Cases

#### Critical Paths:
1. User registration → Login → Dashboard
2. Donor: Add donation → View history → Download certificate
3. Receiver: Search donors → Create request → View requests
4. Admin: Login → Manage users → Export data

---

## 📝 9. Documentation Requirements

### 9.1 User Documentation
- ✅ README.md (Installation & usage)
- ✅ UPDATES.md (Feature changes)
- ✅ ENHANCEMENTS.md (UI improvements)
- ✅ IMPROVEMENTS.md (Latest features)
- ✅ LITERATURE_SURVEY.md (Research & comparison)
- ✅ SYSTEM_REQUIREMENTS.md (This document)

### 9.2 Technical Documentation
- Code comments for complex functions
- API endpoint documentation
- Database schema diagram
- Deployment guide

---

## 🎯 10. Acceptance Criteria

### System Acceptance:
- ✅ All functional requirements implemented
- ✅ Performance meets NFR specifications
- ✅ Security requirements satisfied
- ✅ Cross-browser compatibility verified
- ✅ Mobile responsiveness confirmed
- ✅ Documentation complete
- ✅ Deployment successful
- ✅ User testing positive feedback

---

## 📞 11. Support & Maintenance

### Support Channels:
- **Email**: saimerla633@gmail.com
- **Phone**: 8465989747
- **Developer**: M.ch.v.Sai Phanindhra

### Maintenance Schedule:
- **Updates**: Monthly feature updates
- **Security Patches**: As needed
- **Backups**: Daily automated
- **Monitoring**: 24/7 uptime monitoring

---

**Document Version:** 1.0  
**Last Updated:** January 6, 2026  
**Approved by:** M.ch.v.Sai Phanindhra  
**Next Review:** March 2026
