from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
import secrets
import os
import csv
from io import BytesIO, StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

DATABASE = 'blood_donation.db'
UPLOAD_FOLDER = 'static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database helper functions
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            profile_picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Donor details table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donor_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            blood_group TEXT NOT NULL,
            availability_status TEXT DEFAULT 'available',
            last_donation_date TEXT,
            total_donations INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Blood requests table for urgent requests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blood_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receiver_id INTEGER NOT NULL,
            blood_group TEXT NOT NULL,
            units_needed INTEGER DEFAULT 1,
            urgency TEXT DEFAULT 'normal',
            hospital_name TEXT,
            contact_person TEXT,
            contact_phone TEXT,
            additional_notes TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Donations table for tracking donation history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id INTEGER NOT NULL,
            donation_date DATE NOT NULL,
            blood_group TEXT NOT NULL,
            units_donated REAL DEFAULT 1,
            donation_center TEXT,
            certificate_number TEXT,
            next_eligible_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (donor_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Password reset tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Create default admin user (email: saimerla633@gmail.com, password: RathnamMerla@2004)
    admin_hash = generate_password_hash('RathnamMerla@2004')
    cursor.execute('''
        INSERT OR IGNORE INTO users (name, email, phone, address, role, password_hash, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('M.ch.v.Sai Phanindhra', 'saimerla633@gmail.com', '8465989747', 'Admin Address', 'admin', admin_hash, 'active'))
    
    conn.commit()
    conn.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        role = request.form.get('role')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        blood_group = request.form.get('blood_group')
        
        # Validation
        if not all([name, email, phone, address, role, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        if role == 'donor' and not blood_group:
            flash('Blood group is required for donors.', 'danger')
            return redirect(url_for('register'))
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if email exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            flash('Email already registered.', 'danger')
            conn.close()
            return redirect(url_for('register'))
        
        # Insert user
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (name, email, phone, address, role, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, address, role, password_hash))
        
        user_id = cursor.lastrowid
        
        # If donor, insert donor details
        if role == 'donor':
            cursor.execute('''
                INSERT INTO donor_details (user_id, blood_group, availability_status)
                VALUES (?, ?, ?)
            ''', (user_id, blood_group, 'available'))
        
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        login_role = request.form.get('role', 'user')  # 'user' or 'admin'
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check based on selected role
        if login_role == 'admin':
            cursor.execute('SELECT * FROM users WHERE email = ? AND role = ?', (email, 'admin'))
        else:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            # Verify role matches for admin login
            if login_role == 'admin' and user['role'] != 'admin':
                flash('Invalid admin credentials.', 'danger')
                return redirect(url_for('login'))
            
            if user['status'] == 'blocked':
                flash('Your account has been blocked. Contact administrator.', 'danger')
                return redirect(url_for('login'))
            
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            if login_role == 'admin':
                flash('Invalid admin credentials.', 'danger')
            else:
                flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user details
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # Get donor details if user is donor
    donor_details = None
    if user['role'] == 'donor':
        cursor.execute('SELECT * FROM donor_details WHERE user_id = ?', (session['user_id'],))
        donor_details = cursor.fetchone()
    
    # Get all donors if user is receiver
    donors = []
    if user['role'] == 'receiver':
        cursor.execute('''
            SELECT u.name, u.email, u.phone, u.address, d.blood_group, d.availability_status
            FROM users u
            JOIN donor_details d ON u.id = d.user_id
            WHERE u.role = 'donor' AND u.status = 'active' AND d.availability_status = 'available'
            ORDER BY d.blood_group
        ''')
        donors = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', user=user, donor_details=donor_details, donors=donors)

@app.route('/switch-role', methods=['POST'])
@login_required
def switch_role():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    new_role = 'receiver' if user['role'] == 'donor' else 'donor'
    
    cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, session['user_id']))
    
    # If switching to donor and no donor details exist, create entry
    if new_role == 'donor':
        cursor.execute('SELECT * FROM donor_details WHERE user_id = ?', (session['user_id'],))
        if not cursor.fetchone():
            blood_group = request.form.get('blood_group', 'A+')
            cursor.execute('''
                INSERT INTO donor_details (user_id, blood_group, availability_status)
                VALUES (?, ?, ?)
            ''', (session['user_id'], blood_group, 'available'))
    
    conn.commit()
    conn.close()
    
    session['role'] = new_role
    flash(f'Role switched to {new_role.capitalize()} successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        blood_group = request.form.get('blood_group')
        availability = request.form.get('availability')
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET name = ?, phone = ?, address = ?
            WHERE id = ?
        ''', (name, phone, address, session['user_id']))
        
        # Update donor details if donor
        if session['role'] == 'donor' and blood_group:
            cursor.execute('''
                UPDATE donor_details 
                SET blood_group = ?, availability_status = ?
                WHERE user_id = ?
            ''', (blood_group, availability, session['user_id']))
        
        conn.commit()
        conn.close()
        
        session['name'] = name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    donor_details = None
    if user['role'] == 'donor':
        cursor.execute('SELECT * FROM donor_details WHERE user_id = ?', (session['user_id'],))
        donor_details = cursor.fetchone()
    
    conn.close()
    
    return render_template('edit_profile.html', user=user, donor_details=donor_details)

@app.route('/search-donors', methods=['GET'])
@login_required
def search_donors():
    blood_group = request.args.get('blood_group', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if blood_group:
        cursor.execute('''
            SELECT u.name, u.email, u.phone, u.address, d.blood_group, d.availability_status
            FROM users u
            JOIN donor_details d ON u.id = d.user_id
            WHERE u.role = 'donor' AND u.status = 'active' 
            AND d.availability_status = 'available'
            AND d.blood_group = ?
            ORDER BY d.blood_group
        ''', (blood_group,))
    else:
        cursor.execute('''
            SELECT u.name, u.email, u.phone, u.address, d.blood_group, d.availability_status
            FROM users u
            JOIN donor_details d ON u.id = d.user_id
            WHERE u.role = 'donor' AND u.status = 'active' AND d.availability_status = 'available'
            ORDER BY d.blood_group
        ''')
    
    donors = cursor.fetchall()
    conn.close()
    
    return render_template('search_donors.html', donors=donors, blood_group=blood_group)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND role = ?', (email, 'admin'))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin['password_hash'], password):
            session['user_id'] = admin['id']
            session['name'] = admin['name']
            session['email'] = admin['email']
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get search query if provided
    search_query = request.args.get('query', '').strip()
    
    # Get all users with optional search
    if search_query:
        cursor.execute('''
            SELECT u.*, d.blood_group, d.availability_status, d.total_donations
            FROM users u
            LEFT JOIN donor_details d ON u.id = d.user_id
            WHERE u.role != 'admin' 
            AND (u.name LIKE ? OR u.email LIKE ? OR d.blood_group LIKE ?)
            ORDER BY u.created_at DESC
        ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute('''
            SELECT u.*, d.blood_group, d.availability_status, d.total_donations
            FROM users u
            LEFT JOIN donor_details d ON u.id = d.user_id
            WHERE u.role != 'admin'
            ORDER BY u.created_at DESC
        ''')
    users = cursor.fetchall()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role != "admin"')
    total_users = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "donor" AND status = "active"')
    active_donors = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "receiver" AND status = "active"')
    active_receivers = cursor.fetchone()['count']
    
    # Get blood group distribution
    cursor.execute('''
        SELECT blood_group, COUNT(*) as count
        FROM donor_details d
        JOIN users u ON d.user_id = u.id
        WHERE u.status = 'active'
        GROUP BY blood_group
        ORDER BY count DESC
    ''')
    blood_groups = cursor.fetchall()
    
    # Get total donations
    cursor.execute('SELECT COALESCE(SUM(total_donations), 0) as total FROM donor_details')
    total_donations = cursor.fetchone()['total']
    
    # Get active requests
    cursor.execute('SELECT COUNT(*) as count FROM blood_requests WHERE status = "active"')
    active_requests = cursor.fetchone()['count']
    
    # Get recent registrations (last 30 days)
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM users
        WHERE role != 'admin' AND created_at >= date('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    ''')
    recent_registrations = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         users=users, 
                         total_users=total_users,
                         active_donors=active_donors,
                         active_receivers=active_receivers,
                         blood_groups=blood_groups,
                         total_donations=total_donations,
                         active_requests=active_requests,
                         recent_registrations=recent_registrations)

@app.route('/admin/toggle-status/<int:user_id>')
@admin_required
def toggle_status(user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT status FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    new_status = 'blocked' if user['status'] == 'active' else 'active'
    cursor.execute('UPDATE users SET status = ? WHERE id = ?', (new_status, user_id))
    
    conn.commit()
    conn.close()
    
    flash(f'User status updated to {new_status}.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-user/<int:user_id>')
@admin_required
def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM donor_details WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/search-users')
@admin_required
def search_users():
    search_query = request.args.get('query', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.*, d.blood_group, d.availability_status
        FROM users u
        LEFT JOIN donor_details d ON u.id = d.user_id
        WHERE u.role != 'admin' 
        AND (u.name LIKE ? OR u.email LIKE ? OR d.blood_group LIKE ?)
        ORDER BY u.created_at DESC
    ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    
    users = cursor.fetchall()
    conn.close()
    
    return render_template('admin_search.html', users=users, query=search_query)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/diet-plan')
def diet_plan():
    return render_template('diet_plan.html')

@app.route('/create-request', methods=['GET', 'POST'])
@login_required
def create_request():
    if request.method == 'POST':
        blood_group = request.form.get('blood_group')
        units_needed = request.form.get('units_needed')
        urgency = request.form.get('urgency')
        hospital_name = request.form.get('hospital_name')
        contact_person = request.form.get('contact_person')
        contact_phone = request.form.get('contact_phone')
        additional_notes = request.form.get('additional_notes')
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blood_requests 
            (receiver_id, blood_group, units_needed, urgency, hospital_name, 
             contact_person, contact_phone, additional_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], blood_group, units_needed, urgency, hospital_name,
              contact_person, contact_phone, additional_notes))
        
        conn.commit()
        conn.close()
        
        flash('Blood request created successfully! Donors will be notified.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_request.html')

@app.route('/blood-requests')
@login_required
def blood_requests():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT br.*, u.name as receiver_name, u.email as receiver_email
        FROM blood_requests br
        JOIN users u ON br.receiver_id = u.id
        WHERE br.status = 'active'
        ORDER BY 
            CASE br.urgency
                WHEN 'critical' THEN 1
                WHEN 'urgent' THEN 2
                WHEN 'normal' THEN 3
            END,
            br.created_at DESC
    ''')
    
    requests = cursor.fetchall()
    conn.close()
    
    return render_template('blood_requests.html', requests=requests)

@app.route('/live-stats')
def live_stats():
    """Real-time statistics dashboard"""
    return render_template('live_stats.html')

@app.route('/api/stats')
def api_stats():
    """Real-time statistics API endpoint"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get real-time statistics
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "donor" AND status = "active"')
    total_donors = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "receiver" AND status = "active"')
    total_receivers = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM blood_requests WHERE status = "active"')
    active_requests = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM blood_requests WHERE status = "active" AND urgency = "critical"')
    critical_requests = cursor.fetchone()['count']
    
    cursor.execute('''
        SELECT blood_group, COUNT(*) as count 
        FROM donor_details d
        JOIN users u ON d.user_id = u.id
        WHERE u.status = 'active' AND d.availability_status = 'available'
        GROUP BY blood_group
    ''')
    blood_groups = {row['blood_group']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    
    return jsonify({
        'total_donors': total_donors,
        'total_receivers': total_receivers,
        'active_requests': active_requests,
        'critical_requests': critical_requests,
        'blood_groups': blood_groups,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/recent-requests')
def api_recent_requests():
    """Get recent blood requests for real-time updates"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT br.*, u.name as receiver_name
        FROM blood_requests br
        JOIN users u ON br.receiver_id = u.id
        WHERE br.status = 'active'
        AND br.created_at > datetime('now', '-1 hour')
        ORDER BY br.created_at DESC
        LIMIT 5
    ''')
    
    requests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'requests': requests})

@app.route('/health-checker', methods=['GET', 'POST'])
def health_checker():
    result = None
    bmi = None
    
    if request.method == 'POST':
        try:
            weight = float(request.form.get('weight'))  # in kg
            height = float(request.form.get('height'))  # in cm
            age = int(request.form.get('age'))
            gender = request.form.get('gender')
            
            # Convert height to meters
            height_m = height / 100
            
            # Calculate BMI
            bmi = round(weight / (height_m ** 2), 2)
            
            # Eligibility criteria
            eligible = True
            reasons = []
            
            # Age check (18-65 years)
            if age < 18:
                eligible = False
                reasons.append('Must be at least 18 years old')
            elif age > 65:
                eligible = False
                reasons.append('Must be 65 years or younger')
            
            # Weight check (minimum 50 kg)
            if weight < 50:
                eligible = False
                reasons.append('Minimum weight requirement is 50 kg')
            
            # BMI check
            if bmi < 18.5:
                eligible = False
                reasons.append('BMI is too low (underweight)')
            elif bmi > 30:
                eligible = False
                reasons.append('BMI is too high (may need medical evaluation)')
            
            result = {
                'eligible': eligible,
                'reasons': reasons,
                'weight': weight,
                'height': height,
                'age': age,
                'gender': gender
            }
        except (ValueError, TypeError):
            flash('Please enter valid numeric values.', 'danger')
    
    return render_template('health_checker.html', result=result, bmi=bmi)

@app.route('/upload-profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('edit_profile'))
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('edit_profile'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"user_{session['user_id']}_{secrets.token_hex(8)}.{file.filename.rsplit('.', 1)[1].lower()}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Update database
        conn = get_db()
        cursor = conn.cursor()
        
        # Delete old profile picture if exists
        cursor.execute('SELECT profile_picture FROM users WHERE id = ?', (session['user_id'],))
        old_pic = cursor.fetchone()
        if old_pic and old_pic['profile_picture']:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_pic['profile_picture'])
            if os.path.exists(old_path):
                os.remove(old_path)
        
        cursor.execute('UPDATE users SET profile_picture = ? WHERE id = ?', (filename, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Profile picture updated successfully!', 'success')
    else:
        flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'danger')
    
    return redirect(url_for('edit_profile'))

@app.route('/add-donation', methods=['GET', 'POST'])
@login_required
def add_donation():
    if session.get('role') != 'donor':
        flash('Only donors can add donation records.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        donation_date = request.form.get('donation_date')
        units_donated = request.form.get('units_donated', 1)
        donation_center = request.form.get('donation_center')
        notes = request.form.get('notes')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get donor blood group
        cursor.execute('SELECT blood_group FROM donor_details WHERE user_id = ?', (session['user_id'],))
        donor = cursor.fetchone()
        blood_group = donor['blood_group'] if donor else 'Unknown'
        
        # Calculate next eligible date (3 months after donation)
        donation_dt = datetime.strptime(donation_date, '%Y-%m-%d')
        next_eligible_date = donation_dt + timedelta(days=90)
        
        # Generate certificate number
        certificate_number = f"BDN{datetime.now().year}{session['user_id']:04d}{secrets.token_hex(4).upper()}"
        
        # Insert donation record
        cursor.execute('''
            INSERT INTO donations 
            (donor_id, donation_date, blood_group, units_donated, donation_center, 
             certificate_number, next_eligible_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], donation_date, blood_group, units_donated, 
              donation_center, certificate_number, next_eligible_date, notes))
        
        # Update total donations count
        cursor.execute('''
            UPDATE donor_details 
            SET total_donations = total_donations + 1,
                last_donation_date = ?
            WHERE user_id = ?
        ''', (donation_date, session['user_id']))
        
        conn.commit()
        conn.close()
        
        flash(f'Donation record added successfully! Certificate #: {certificate_number}', 'success')
        return redirect(url_for('donation_history'))
    
    return render_template('add_donation.html')

@app.route('/donation-history')
@login_required
def donation_history():
    if session.get('role') != 'donor':
        flash('Only donors can view donation history.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all donations for this donor
    cursor.execute('''
        SELECT * FROM donations
        WHERE donor_id = ?
        ORDER BY donation_date DESC
    ''', (session['user_id'],))
    donations = cursor.fetchall()
    
    # Get donor details for badge calculation
    cursor.execute('SELECT total_donations FROM donor_details WHERE user_id = ?', (session['user_id'],))
    donor = cursor.fetchone()
    total_donations = donor['total_donations'] if donor else 0
    
    # Calculate badge
    badge = None
    badge_color = None
    if total_donations >= 50:
        badge = 'Platinum Donor'
        badge_color = '#E5E4E2'
    elif total_donations >= 25:
        badge = 'Gold Donor'
        badge_color = '#FFD700'
    elif total_donations >= 10:
        badge = 'Silver Donor'
        badge_color = '#C0C0C0'
    elif total_donations >= 5:
        badge = 'Bronze Donor'
        badge_color = '#CD7F32'
    elif total_donations >= 1:
        badge = 'Hero Donor'
        badge_color = '#4CAF50'
    
    conn.close()
    
    return render_template('donation_history.html', 
                         donations=donations, 
                         total_donations=total_donations,
                         badge=badge,
                         badge_color=badge_color)

@app.route('/download-certificate/<int:donation_id>')
@login_required
def download_certificate(donation_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT d.*, u.name as donor_name
        FROM donations d
        JOIN users u ON d.donor_id = u.id
        WHERE d.id = ? AND d.donor_id = ?
    ''', (donation_id, session['user_id']))
    
    donation = cursor.fetchone()
    conn.close()
    
    if not donation:
        flash('Donation record not found.', 'danger')
        return redirect(url_for('donation_history'))
    
    # Generate PDF certificate
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Draw certificate
    # Border
    p.setLineWidth(3)
    p.setStrokeColorRGB(0.9, 0.22, 0.27)
    p.rect(0.5*inch, 0.5*inch, width-inch, height-inch)
    
    # Title
    p.setFont("Helvetica-Bold", 30)
    p.setFillColorRGB(0.9, 0.22, 0.27)
    p.drawCentredString(width/2, height-2*inch, "CERTIFICATE OF APPRECIATION")
    
    # Subtitle
    p.setFont("Helvetica", 16)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(width/2, height-2.5*inch, "Blood Donation Network")
    
    # Body text
    p.setFont("Helvetica", 14)
    p.drawCentredString(width/2, height-3.5*inch, "This is to certify that")
    
    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.9, 0.22, 0.27)
    p.drawCentredString(width/2, height-4*inch, donation['donor_name'])
    
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(width/2, height-4.5*inch, "has generously donated blood")
    
    # Details
    p.setFont("Helvetica-Bold", 12)
    details_y = height - 5.5*inch
    p.drawString(2*inch, details_y, f"Blood Group: {donation['blood_group']}")
    p.drawString(2*inch, details_y - 0.3*inch, f"Units Donated: {donation['units_donated']}")
    p.drawString(2*inch, details_y - 0.6*inch, f"Donation Date: {donation['donation_date']}")
    p.drawString(2*inch, details_y - 0.9*inch, f"Certificate Number: {donation['certificate_number']}")
    
    # Footer
    p.setFont("Helvetica-Italic", 10)
    p.drawCentredString(width/2, 1.5*inch, "Your donation saves lives. Thank you for being a hero!")
    
    # Signature line
    p.setFont("Helvetica", 10)
    p.line(width/2 + inch, inch, width - 1.5*inch, inch)
    p.drawCentredString(width/2 + 2*inch, 0.7*inch, "Authorized Signature")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'donation_certificate_{donation["certificate_number"]}.pdf', mimetype='application/pdf')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)
            
            cursor.execute('''
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user['id'], token, expires_at))
            conn.commit()
            
            # In production, send email with reset link
            reset_link = url_for('reset_password', token=token, _external=True)
            flash(f'Password reset link (for development): {reset_link}', 'info')
        else:
            # Don't reveal if email exists or not for security
            flash('If your email is registered, you will receive a password reset link.', 'info')
        
        conn.close()
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM password_reset_tokens
        WHERE token = ? AND used = 0 AND expires_at > ?
    ''', (token, datetime.now()))
    
    reset_token = cursor.fetchone()
    
    if not reset_token:
        conn.close()
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('reset_password.html', token=token)
        
        # Update password
        password_hash = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                      (password_hash, reset_token['user_id']))
        
        # Mark token as used
        cursor.execute('UPDATE password_reset_tokens SET used = 1 WHERE id = ?', 
                      (reset_token['id'],))
        
        conn.commit()
        conn.close()
        
        flash('Password reset successfully! Please login with your new password.', 'success')
        return redirect(url_for('login'))
    
    conn.close()
    return render_template('reset_password.html', token=token)

@app.route('/admin/export-users')
@admin_required
def export_users():
    """Export all users to CSV"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id, u.name, u.email, u.phone, u.address, u.role, u.status,
               d.blood_group, d.availability_status, d.total_donations, u.created_at
        FROM users u
        LEFT JOIN donor_details d ON u.id = d.user_id
        WHERE u.role != 'admin'
        ORDER BY u.created_at DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Address', 'Role', 'Status', 
                     'Blood Group', 'Availability', 'Total Donations', 'Joined Date'])
    
    for user in users:
        writer.writerow([
            user['id'], user['name'], user['email'], user['phone'], user['address'],
            user['role'], user['status'], user['blood_group'] or 'N/A',
            user['availability_status'] or 'N/A', user['total_donations'] or 0,
            user['created_at'][:10]
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=users_export_{datetime.now().strftime('%Y%m%d')}.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
