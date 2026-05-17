import re
import os
from werkzeug.utils import secure_filename

class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        pattern = r'^[0-9]{10,15}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_file_extension(filename, allowed_extensions=None):
        """Validate file extension"""
        if allowed_extensions is None:
            allowed_extensions = {'png', 'jpg', 'jpeg', 'dcm', 'nii'}
        
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def validate_file_size(file, max_size_mb=10):
        """Validate file size"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        max_bytes = max_size_mb * 1024 * 1024
        return size <= max_bytes
    
    @staticmethod
    def validate_age(age):
        """Validate age"""
        return isinstance(age, (int, float)) and 0 <= age <= 120
    
    @staticmethod
    def sanitize_input(text):
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove any HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        # Escape special characters
        text = re.sub(r'[;&|`$]', '', text)
        
        return text.strip()
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength"""
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Optional: Add more strength checks
        # has_upper = any(c.isupper() for c in password)
        # has_lower = any(c.islower() for c in password)
        # has_digit = any(c.isdigit() for c in password)
        # has_special = any(c in '!@#$%^&*' for c in password)
        
        return True, "Password is valid"