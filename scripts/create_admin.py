#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.models import db, User
from flask_bcrypt import Bcrypt
from app import create_app

def create_admin_user():
    """Create admin user if not exists"""
    app = create_app()
    bcrypt = Bcrypt()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(role='admin').first()
        
        if admin:
            print(f"Admin user already exists: {admin.email}")
            return
        
        # Create admin user
        admin = User(
            user_id='ADMIN001',
            name='System Administrator',
            email='admin@cancerdetection.com',
            password_hash=bcrypt.generate_password_hash('Admin@123').decode('utf-8'),
            role='admin',
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Email: admin@cancerdetection.com")
        print("Password: Admin@123")
        
        # Also create a sample doctor
        doctor = User.query.filter_by(role='doctor').first()
        
        if not doctor:
            doctor = User(
                user_id='DOC001',
                name='Dr. Sarah Johnson',
                email='sarah.johnson@hospital.com',
                password_hash=bcrypt.generate_password_hash('Doctor@123').decode('utf-8'),
                role='doctor',
                specialization='Oncology',
                hospital_name='City General Hospital',
                is_active=True
            )
            
            db.session.add(doctor)
            db.session.commit()
            
            print("\nSample doctor created successfully!")
            print("Email: sarah.johnson@hospital.com")
            print("Password: Doctor@123")

if __name__ == '__main__':
    create_admin_user()
    print("\nSetup complete! You can now run the application with:")
    print("python app.py")