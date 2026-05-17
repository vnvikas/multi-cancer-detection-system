#!/usr/bin/env python
import os
import datetime
import subprocess
from dotenv import load_dotenv

load_dotenv()

def backup_database():
    """Backup MySQL database"""
    db_name = os.environ.get('DB_NAME', 'multi_cancer_db')
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', 'localhost')
    
    # Create backup directory
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'{db_name}_{timestamp}.sql')
    
    # Create backup command
    if db_password:
        cmd = f'mysqldump -h {db_host} -u {db_user} -p{db_password} {db_name} > {backup_file}'
    else:
        cmd = f'mysqldump -h {db_host} -u {db_user} {db_name} > {backup_file}'
    
    # Execute backup
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Database backup created: {backup_file}")
        
        # Compress backup
        compress_cmd = f'gzip {backup_file}'
        subprocess.run(compress_cmd, shell=True, check=True)
        print(f"Backup compressed: {backup_file}.gz")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Backup failed: {e}")
        return False

if __name__ == '__main__':
    backup_database()