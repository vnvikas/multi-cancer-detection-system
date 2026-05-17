# save as generate_hashes.py
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Generate hash for Admin@123
admin_hash = bcrypt.generate_password_hash('Admin@123').decode('utf-8')
print(f"Admin Password (Admin@123) Hash: {admin_hash}")

# Generate hash for Doctor@123
doctor_hash = bcrypt.generate_password_hash('Doctor@123').decode('utf-8')
print(f"Doctor Password (Doctor@123) Hash: {doctor_hash}")

# Generate hash for test password
test_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
print(f"Test Password (password123) Hash: {test_hash}")