import sqlite3
from werkzeug.security import check_password_hash

# Connect to database
conn = sqlite3.connect('blood_donation.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check admin user
cursor.execute("SELECT * FROM users WHERE email = ? AND role = ?", ('saimerla633@gmail.com', 'admin'))
admin = cursor.fetchone()

if admin:
    print("✅ Admin user found in database!")
    print(f"Name: {admin['name']}")
    print(f"Email: {admin['email']}")
    print(f"Phone: {admin['phone']}")
    print(f"Role: {admin['role']}")
    print(f"Status: {admin['status']}")
    
    # Test password
    password = 'RathnamMerla@2004'
    if check_password_hash(admin['password_hash'], password):
        print(f"✅ Password verification SUCCESSFUL for: {password}")
    else:
        print(f"❌ Password verification FAILED for: {password}")
else:
    print("❌ Admin user NOT found in database!")

conn.close()
