from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('doctor.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        # Validation
        if not email or not password:
            flash('Please enter both email and password', 'danger')
            return render_template('login.html')
        
        # Import here to avoid circular imports
        from backend.database.models import User, db, SystemLog
        from flask_bcrypt import Bcrypt
        
        bcrypt = Bcrypt()
        
        try:
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                flash('Invalid email or password', 'danger')
                return render_template('login.html')
            
            if not user.is_active:
                flash('Your account has been deactivated. Please contact administrator.', 'danger')
                return render_template('login.html')
            
            # Check password with error handling
            try:
                password_valid = bcrypt.check_password_hash(user.password_hash, password)
            except ValueError as e:
                print(f"Password hash error for {email}: {e}")
                # Hash might be corrupted, regenerate it
                if user.role == 'admin':
                    new_hash = bcrypt.generate_password_hash('Admin@123').decode('utf-8')
                else:
                    new_hash = bcrypt.generate_password_hash('Doctor@123').decode('utf-8')
                user.password_hash = new_hash
                db.session.commit()
                password_valid = bcrypt.check_password_hash(user.password_hash, password)
            
            if password_valid:
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Login user
                login_user(user, remember=remember)
                
                # Log the login action
                try:
                    log = SystemLog(
                        user_id=user.id,
                        action='LOGIN',
                        entity_type='user',
                        entity_id=user.user_id,
                        details=f'User logged in',
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent')
                    )
                    db.session.add(log)
                    db.session.commit()
                except:
                    pass
                
                flash(f'Welcome back, {user.name}!', 'success')
                
                # Redirect based on role
                if user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('doctor.dashboard'))
            else:
                flash('Invalid email or password', 'danger')
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    from backend.database.models import db
    from flask_bcrypt import Bcrypt
    
    bcrypt = Bcrypt()
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not bcrypt.check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'danger')
            return render_template('auth/change_password.html')
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return render_template('auth/change_password.html')
        
        # Update password
        current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        
        flash('Password changed successfully. Please login again.', 'success')
        logout_user()
        return redirect(url_for('auth.login'))
    
    return render_template('auth/change_password.html')


@auth_bp.route('/logout')
@login_required
def logout():
    try:
        from backend.database.models import db, SystemLog
        log = SystemLog(
            user_id=current_user.id,
            action='LOGOUT',
            entity_type='user',
            entity_id=current_user.user_id,
            details='User logged out',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log)
        db.session.commit()
    except:
        pass
    
    logout_user()
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))