import unittest
import os
import sys
import sqlite3

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.app import create_app
from App.database import get_db_connection, DictAndTupleRow
from App.routes import extract_count
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

class DashboardCountTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        conn = get_db_connection()
        c = conn.cursor()

        # Set up a test user
        c.execute("SELECT id FROM users WHERE username = %s", ('dash_user@example.com',))
        user = c.fetchone()
        if not user:
            c.execute("INSERT INTO users (username, password, fullname, role) VALUES (%s, %s, %s, 'USER')",
                      ('dash_user@example.com', generate_password_hash('password123'), 'Dash User'))
            conn.commit()
            c.execute("SELECT id FROM users WHERE username = %s", ('dash_user@example.com',))
            user = c.fetchone()
        
        self.user_id = user['id'] if isinstance(user, dict) or hasattr(user, '__getitem__') else user[0]

        # Clean prior test predictions for this user
        c.execute("DELETE FROM predictions WHERE user_id = %s", (self.user_id,))
        
        # Insert test predictions: 2 Fake, 1 Real
        c.execute("INSERT INTO predictions (user_id, input_text, prediction_result) VALUES (%s, %s, %s)",
                  (self.user_id, 'Sample job posting 1', 'Fake (Confidence: 94%)'))
        c.execute("INSERT INTO predictions (user_id, input_text, prediction_result) VALUES (%s, %s, %s)",
                  (self.user_id, 'Sample job posting 2', 'Fake'))
        c.execute("INSERT INTO predictions (user_id, input_text, prediction_result) VALUES (%s, %s, %s)",
                  (self.user_id, 'Sample job posting 3', 'Real (Confidence: 98%)'))
        conn.commit()
        c.close()
        conn.close()

    def tearDown(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM predictions WHERE user_id = %s", (self.user_id,))
        c.execute("DELETE FROM users WHERE username = %s", ('dash_user@example.com',))
        conn.commit()
        c.close()
        conn.close()

    def test_extract_count_with_various_types(self):
        """Test extract_count with all expected row formats."""
        # 1. Dict with 'count'
        self.assertEqual(extract_count({'count': 42}), 42)
        # 2. Tuple
        self.assertEqual(extract_count((17,)), 17)
        # 3. None
        self.assertEqual(extract_count(None), 0)
        # 4. Int / float
        self.assertEqual(extract_count(5), 5)
        self.assertEqual(extract_count(5.0), 5)
        
        # 5. sqlite3.Row with AS count
        s_conn = sqlite3.connect(':memory:')
        s_conn.row_factory = sqlite3.Row
        s_cur = s_conn.cursor()
        s_cur.execute("SELECT 10 AS count")
        s_row = s_cur.fetchone()
        self.assertEqual(extract_count(s_row), 10)

        # 6. sqlite3.Row without AS count (keys = ['COUNT(*)'])
        s_cur.execute("SELECT COUNT(*) FROM (SELECT 1 UNION ALL SELECT 2)")
        s_row_no_alias = s_cur.fetchone()
        self.assertEqual(extract_count(s_row_no_alias), 2)
        s_conn.close()

        # 7. DictAndTupleRow
        class MockDescCursor:
            description = [('count', 23, None, None, None, None, None)]
        dt_row = DictAndTupleRow(MockDescCursor(), (8,))
        self.assertEqual(extract_count(dt_row), 8)
        self.assertEqual(dt_row['count'], 8)
        self.assertEqual(dt_row[0], 8)

        # 8. DictAndTupleRow without alias (column name 'COUNT(*)')
        class MockDescCursor2:
            description = [('COUNT(*)', 23, None, None, None, None, None)]
        dt_row2 = DictAndTupleRow(MockDescCursor2(), (15,))
        self.assertEqual(extract_count(dt_row2), 15)
        self.assertEqual(dt_row2['count'], 15)
        self.assertEqual(dt_row2[0], 15)

    def test_dashboard_route_success(self):
        """Test the Flask /dashboard route executes without IndexError and computes counts correctly."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
            sess['username'] = 'dash_user@example.com'
            sess['role'] = 'USER'

        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        # Check that total scans (3) and fake found (2) are rendered
        self.assertIn('3', content)
        self.assertIn('2', content)

    def test_api_dashboard_route_success(self):
        """Test /api/dashboard returns correct counts for user scans and fake jobs."""
        with self.app.app_context():
            token = create_access_token(identity='dash_user@example.com')

        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/dashboard', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['total_scans'], 3)
        self.assertEqual(data['fake_found'], 2)
        self.assertEqual(data['real_found'], 1)
        self.assertEqual(len(data['history']), 3)

    def test_admin_and_api_admin_count_queries(self):
        """Test admin and api/admin routes execute COUNT queries successfully."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'ADMIN'

        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            token = create_access_token(identity='admin')

        headers = {'Authorization': f'Bearer {token}'}
        api_response = self.client.get('/api/admin', headers=headers)
        self.assertEqual(api_response.status_code, 200)
        data = api_response.get_json()
        self.assertIn('total_users', data)
        self.assertIn('total_admins', data)
        self.assertIn('total_predictions', data)
        self.assertIn('fake_detected', data)

if __name__ == '__main__':
    unittest.main()
