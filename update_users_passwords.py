# save as update_users_passwords.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from backend.database.models import db, User
from flask_bcrypt import Bcrypt

def update_users_passwords():
    app = create_app()
    bcrypt = Bcrypt()
    
    with app.app_context():
        # Get all existing users
        users = User.query.all()
        
        if not users:
            print("No users found in database!")
            return
        
        print(f"Found {len(users)} users in database\n")
        
        # Update each user's password
        for user in users:
            print(f"Updating user: {user.email}")
            
            if user.role == 'admin':
                new_password = 'Admin@123'
            else:
                new_password = 'Doctor@123'
            
            # Generate new hash
            new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password_hash = new_hash
            user.is_active = True
            
            print(f"  New hash generated: {new_hash[:40]}...")
        
        # Commit changes
        db.session.commit()
        
        print("\n" + "="*50)
        print("✅ PASSWORDS UPDATED SUCCESSFULLY!")
        print("="*50)
        
        # Verify
        print("\n=== VERIFICATION ===")
        for user in User.query.all():
            if user.role == 'admin':
                is_valid = bcrypt.check_password_hash(user.password_hash, 'Admin@123')
                print(f"Admin ({user.email}) password valid: {is_valid}")
            else:
                is_valid = bcrypt.check_password_hash(user.password_hash, 'Doctor@123')
                print(f"Doctor ({user.email}) password valid: {is_valid}")
        
        print("\n" + "="*50)
        print("LOGIN CREDENTIALS:")
        print("="*50)
        print("Admin:  admin@cancerdetection.com / Admin@123")
        print("Doctor: sarah.johnson@hospital.com / Doctor@123")
        print("="*50)

if __name__ == '__main__':
    update_users_passwords()