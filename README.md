# Blood Donation Network Web Application

A complete, professional Blood Donation Network web application built with Flask, SQLite, and Bootstrap 5. This platform connects blood donors with receivers, featuring user management, role-based dashboards, and a comprehensive admin panel.

## 🩸 Features

### User Features
- **User Registration & Authentication**
  - Secure registration with role selection (Donor/Receiver)
  - Email and password-based login
  - Profile management with editable information

- **Donor Dashboard**
  - Display blood group and availability status
  - Update availability (Available/Unavailable)
  - View donation tips and information
  - Switch to Receiver role anytime

- **Receiver Dashboard**
  - Search for donors by blood group
  - View available donors with contact information
  - Blood compatibility reference guide
  - Switch to Donor role anytime

- **Role Switching**
  - Users can switch between Donor and Receiver roles
  - Blood group information preserved when switching back
  - Seamless role transition

### Admin Features
- **Admin Panel**
  - Separate admin login portal
  - View all registered users
  - Search users by name, email, or blood group
  - Block/unblock user accounts
  - Delete users permanently
  - View statistics (total users, active donors, active receivers)
  - Manage donor availability status

### Security
- Password hashing using Werkzeug security
- Session-based authentication
- Role-based access control
- Protected routes with decorators
- SQL injection prevention

## 🎨 Design

- **Professional Medical Theme**
  - Red, white, and light gray color palette
  - Modern, responsive layout using Bootstrap 5
  - Font Awesome icons
  - Smooth animations and transitions
  - Mobile-friendly design

## 📁 Project Structure

```
blood_donation_network/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── blood_donation.db          # SQLite database (auto-created)
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navbar
│   ├── index.html             # Home page with hero section
│   ├── login.html             # User login page
│   ├── register.html          # User registration page
│   ├── dashboard.html         # User dashboard
│   ├── edit_profile.html      # Profile editing page
│   ├── search_donors.html     # Donor search page
│   ├── admin_login.html       # Admin login page
│   ├── admin_dashboard.html   # Admin dashboard
│   └── admin_search.html      # Admin search results
│
└── static/                     # Static files
    ├── css/
    │   └── style.css          # Custom CSS styling
    └── js/
        └── main.js            # JavaScript functionality
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation Steps

1. **Navigate to the project directory:**
   ```powershell
   cd blood_donation_network
   ```

2. **Create a virtual environment (recommended):**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install required packages:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```powershell
   python app.py
   ```

6. **Open your browser and navigate to:**
   ```
   http://127.0.0.1:5000
   ```

## 👤 Admin Credentials

```


**⚠️ Important:** Keep these credentials secure and change the password periodically!

## 🗄️ Database Schema

### Users Table
- `id` - Primary key
- `name` - User's full name
- `email` - Unique email address
- `phone` - Contact number
- `address` - User's address
- `role` - User role (donor/receiver/admin)
- `password_hash` - Hashed password
- `status` - Account status (active/blocked)
- `created_at` - Registration timestamp

### Donor Details Table
- `id` - Primary key
- `user_id` - Foreign key to users table
- `blood_group` - Blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)
- `availability_status` - Availability (available/unavailable)
- `last_donation_date` - Last donation date (optional)

## 🎯 Usage Guide

### For Donors
1. Register with blood group information
2. Login to your dashboard
3. Update availability status
4. Keep contact information current
5. Respond to receivers promptly

### For Receivers
1. Register as a receiver
2. Login to your dashboard
3. Search for donors by blood group
4. View donor contact information
5. Contact donors directly

### For Administrators
1. Login at `/admin/login`
2. View all users and statistics
3. Search users by various criteria
4. Block/unblock users as needed
5. Delete inactive or fake accounts
6. Monitor donor availability

## 🔧 Configuration

### Change Secret Key
In `app.py`, update the secret key for production:
```python
app.secret_key = 'your-unique-secret-key-here'
```

### Database Location
Default: `blood_donation.db` in project root
To change, update the `DATABASE` variable in `app.py`

## 🌐 Routes

### Public Routes
- `/` - Home page
- `/login` - User login
- `/register` - User registration
- `/admin/login` - Admin login

### Protected Routes (Login Required)
- `/dashboard` - User dashboard
- `/edit-profile` - Edit user profile
- `/search-donors` - Search donors
- `/switch-role` - Switch user role
- `/logout` - Logout

### Admin Routes (Admin Access Only)
- `/admin/dashboard` - Admin dashboard
- `/admin/search-users` - Search users
- `/admin/toggle-status/<user_id>` - Block/unblock user
- `/admin/delete-user/<user_id>` - Delete user

## 🎨 Customization

### Colors
Edit `static/css/style.css` CSS variables:
```css
:root {
    --primary-red: #dc3545;
    --dark-red: #b02a37;
    --light-red: #f8d7da;
}
```

### Logo/Branding
Update navbar in `templates/base.html`

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🔒 Security Best Practices

1. Change the default admin password
2. Update the Flask secret key
3. Use HTTPS in production
4. Regularly backup the database
5. Implement rate limiting for login attempts
6. Add email verification for new users
7. Enable two-factor authentication (optional)

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors, delete `blood_donation.db` and restart the application.

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Dependencies Not Installing
Ensure pip is updated:
```powershell
python -m pip install --upgrade pip
```

## 📝 License

This project is open-source and available for educational purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Support

For support or questions, contact the administrator.

## 🌟 Acknowledgments

- Bootstrap 5 for UI components
- Font Awesome for icons
- Flask framework
- SQLite database

---

**Made with ❤️ for saving lives through blood donation**
