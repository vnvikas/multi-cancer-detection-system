import hashlib
import secrets
import string
from datetime import datetime, timedelta
import os

def generate_random_string(length=8):
    """Generate random string"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_patient_id():
    """Generate unique patient ID"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = generate_random_string(4).upper()
    return f"PAT{timestamp}{random_part}"

def generate_scan_id():
    """Generate unique scan ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = generate_random_string(4).upper()
    return f"SCN{timestamp}{random_part}"

def generate_prediction_id():
    """Generate unique prediction ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = generate_random_string(4).upper()
    return f"PRD{timestamp}{random_part}"

def calculate_age(dob):
    """Calculate age from date of birth"""
    if not dob:
        return None
    today = datetime.now().date()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def format_currency(amount):
    """Format currency"""
    return f"${amount:,.2f}"

def get_percentile(score, max_score=100):
    """Calculate percentile"""
    return (score / max_score) * 100

def hash_file(filepath):
    """Calculate file hash"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_size(filepath):
    """Get file size in human readable format"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"