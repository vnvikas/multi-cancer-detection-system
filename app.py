from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import logging
from datetime import datetime
from config import Config
from flask import send_from_directory

# Initialize extensions AFTER app creation
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    from backend.database.models import db
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page'
    
    # Configure upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
    
    # Setup logging
    if not app.debug:
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.admin import admin_bp
    from backend.routes.doctor import doctor_bp
    from backend.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Main routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('doctor.dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
     return send_from_directory('uploads', filename)
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from backend.database.models import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from backend.database.models import User
    from backend.database.models import db
    # Use Session.get() instead of Query.get() for SQLAlchemy 2.0 compatibility
    return db.session.get(User, int(user_id))

# Create app instance
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from backend.database.models import db
        db.create_all()
        print("Database tables created/verified successfully!")
    
    print("\n" + "="*60)
    print("MULTI-CANCER DETECTION SYSTEM")
    print("="*60)
    print("Server running at: http://localhost:5000")
    print("\nLogin Credentials:")
    print("  Admin: admin@cancerdetection.com / Admin@123")
    print("  Doctor: sarah.johnson@hospital.com / Doctor@123")
    print("\nPress CTRL+C to quit")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)