import sqlite3
from werkzeug.security import generate_password_hash

# Connect to database
conn = sqlite3.connect('blood_donation.db')
cursor = conn.cursor()

# Check if admin exists
cursor.execute("SELECT * FROM users WHERE email = 'saimerla633@gmail.com'")
existing = cursor.fetchone()

if existing:
    print("Admin user already exists, deleting it...")
    cursor.execute("DELETE FROM users WHERE email = 'saimerla633@gmail.com'")

# Create new admin user
print("Creating admin user...")
admin_hash = generate_password_hash('RathnamMerla@2004')
cursor.execute('''
    INSERT INTO users (name, email, phone, address, role, password_hash, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('M.ch.v.Sai Phanindhra', 'saimerla633@gmail.com', '8465989747', 'Admin Address', 'admin', admin_hash, 'active'))

conn.commit()

# Verify
cursor.execute("SELECT * FROM users WHERE email = 'saimerla633@gmail.com' AND role = 'admin'")
admin = cursor.fetchone()

if admin:
    print("✅ Admin user created successfully!")
    print(f"Email: saimerla633@gmail.com")
    print(f"Password: RathnamMerla@2004")
else:
    print("❌ Failed to create admin user!")

conn.close()
