from backend.routes.auth import auth_bp
from backend.routes.admin import admin_bp
from backend.routes.doctor import doctor_bp
from backend.routes.api import api_bp

__all__ = ['auth_bp', 'admin_bp', 'doctor_bp', 'api_bp']