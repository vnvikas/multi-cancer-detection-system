import logging
import os
from datetime import datetime

def setup_logger(name, log_file='app.log', level=logging.INFO):
    """Setup logger with file and console handlers"""
    
    # Create logs directory if not exists
    os.makedirs('logs', exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(f'logs/{log_file}')
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_action(logger, user_id, action, entity_type, entity_id, details, ip_address=None):
    """Log user action to database"""
    from backend.database.models import db, SystemLog
    
    log = SystemLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address
    )
    
    db.session.add(log)
    db.session.commit()
    
    logger.info(f"Action logged: {action} - {details}")