# save as fix_users_complete.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from backend.database.models import db, User
from flask_bcrypt import Bcrypt

def fix_users_complete():
    app = create_app()
    bcrypt = Bcrypt()
    
    with app.app_context():
        # Delete all existing users
        print("Deleting all existing users...")
        User.query.delete()
        db.session.commit()
        print("All users deleted.")
        
        # Create Admin User with proper hash
        print("\nCreating Admin User...")
        admin_password = 'Admin@123'
        admin_hash = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        
        admin = User(
            user_id='ADMIN001',
            name='System Administrator',
            email='admin@cancerdetection.com',
            password_hash=admin_hash,
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        print(f"Admin created with hash: {admin_hash[:40]}...")
        
        # Create Doctor User 1
        print("\nCreating Doctor User...")
        doctor_password = 'Doctor@123'
        doctor_hash = bcrypt.generate_password_hash(doctor_password).decode('utf-8')
        
        doctor = User(
            user_id='DOC001',
            name='Dr. Sarah Johnson',
            email='sarah.johnson@hospital.com',
            password_hash=doctor_hash,
            role='doctor',
            specialization='Oncology',
            hospital_name='City General Hospital',
            is_active=True
        )
        db.session.add(doctor)
        print(f"Doctor created with hash: {doctor_hash[:40]}...")
        
        # Create Doctor User 2
        doctor2 = User(
            user_id='DOC002',
            name='Dr. Michael Chen',
            email='michael.chen@hospital.com',
            password_hash=doctor_hash,
            role='doctor',
            specialization='Radiology',
            hospital_name='Memorial Medical Center',
            is_active=True
        )
        db.session.add(doctor2)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("✅ USERS FIXED SUCCESSFULLY!")
        print("="*50)
        
        # Verify
        print("\n=== VERIFICATION ===")
        admin_check = User.query.filter_by(email='admin@cancerdetection.com').first()
        if admin_check:
            is_valid = bcrypt.check_password_hash(admin_check.password_hash, 'Admin@123')
            print(f"Admin password valid: {is_valid}")
        
        doctor_check = User.query.filter_by(email='sarah.johnson@hospital.com').first()
        if doctor_check:
            is_valid = bcrypt.check_password_hash(doctor_check.password_hash, 'Doctor@123')
            print(f"Doctor password valid: {is_valid}")
        
        print("\n" + "="*50)
        print("LOGIN CREDENTIALS:")
        print("="*50)
        print("Admin:  admin@cancerdetection.com / Admin@123")
        print("Doctor: sarah.johnson@hospital.com / Doctor@123")
        print("Doctor2: michael.chen@hospital.com / Doctor@123")
        print("="*50)

if __name__ == '__main__':
    fix_users_complete()