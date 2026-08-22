import unittest
import json
import os
import sys
from werkzeug.security import generate_password_hash

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.app import create_app
from App.config import Config
from App.database import init_db, get_db_connection

class JWTTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for API tests
        self.client = self.app.test_client()
        
        # Initialize DB and seed test user
        with self.app.app_context():
            init_db()
            conn = get_db_connection()
            c = conn.cursor()
            # Clear test user if already exists to ensure a clean insert
            c.execute("DELETE FROM users WHERE username = %s", ('jwtuser',))
            c.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                      ('jwtuser', generate_password_hash('testpassword'), 'USER'))
            conn.commit()
            c.close()
            conn.close()

    def tearDown(self):
        # Clean up database records
        with self.app.app_context():
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("DELETE FROM users WHERE username = %s", ('jwtuser',))
                conn.commit()
                c.close()
                conn.close()
            except Exception:
                pass

    def test_jwt_flow(self):
        # 1. Try to access /predict without token
        response = self.client.post('/predict', json={'job_description': 'test job'})
        self.assertEqual(response.status_code, 401)
        
        # 2. Login to get token
        response = self.client.post('/api/login', json={
            'username': 'jwtuser', 
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        token = data['access_token']
        
        # 3. Access /predict with token
        headers = {
            'Authorization': f'Bearer {token}'
        }
        # Note: /predict expects 'job_description'
        response = self.client.post('/predict', 
                                   json={'job_description': 'This is a test job description for verification.'},
                                   headers=headers)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('prediction', result)
        
        # 4. Login with bad credentials
        response = self.client.post('/api/login', json={
            'username': 'jwtuser', 
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
