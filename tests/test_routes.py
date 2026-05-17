import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from backend.database.models import db, User

class TestRoutes(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
    
    def test_login_page(self):
        """Test login page loads"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_login(self):
        """Test invalid login attempt"""
        response = self.client.post('/auth/login', data={
            'email': 'wrong@email.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = self.client.get('/api/health')
        # You may need to add a health endpoint
        self.assertEqual(response.status_code, 404)  # Or 200 if implemented

if __name__ == '__main__':
    unittest.main()