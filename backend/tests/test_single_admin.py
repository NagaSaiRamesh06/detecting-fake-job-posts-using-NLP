import unittest
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.app import create_app
from App.config import Config
from App.database import get_db_connection, init_db
from App.fix_admin import fix_admin
from werkzeug.security import generate_password_hash, check_password_hash

class SingleAdminTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        # Ensure normal test user exists with known password
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = %s", ('norm_test_user@example.com',))
        if not c.fetchone():
            c.execute("INSERT INTO users (username, password, fullname, role) VALUES (%s, %s, %s, 'USER')",
                      ('norm_test_user@example.com', generate_password_hash('password123'), 'Normal User'))
            conn.commit()
        else:
            c.execute("UPDATE users SET password = %s, role = 'USER' WHERE username = %s",
                      (generate_password_hash('password123'), 'norm_test_user@example.com'))
            conn.commit()
        c.close()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE username IN (%s, %s)", 
                      ('norm_test_user@example.com', 'brand_new_person@gmail.com'))
            conn.commit()
            c.close()
            conn.close()
        except Exception:
            pass

    def test_01_exactly_one_admin_exists(self):
        """Verify that exactly one admin account exists in the database."""
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, role FROM users WHERE role = 'ADMIN'")
        admins = c.fetchall()
        c.close()
        conn.close()

        self.assertEqual(len(admins), 1, f"Expected exactly 1 admin, found {len(admins)}: {admins}")
        self.assertEqual(admins[0]['username'], getattr(Config, 'ADMIN_USERNAME', 'admin'))

    def test_02_primary_admin_can_login(self):
        """Verify that primary admin can log in with existing credentials."""
        admin_user = getattr(Config, 'ADMIN_USERNAME', 'admin')
        admin_pwd = getattr(Config, 'ADMIN_DEFAULT_PASSWORD', 'admin')

        # Test Session Login
        response = self.client.post('/', data={
            'username': admin_user,
            'password': admin_pwd
        }, follow_redirects=False)
        # Should redirect to admin dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin', response.headers.get('Location', ''))

        # Test API Login
        api_resp = self.client.post('/api/login', json={
            'username': admin_user,
            'password': admin_pwd
        })
        self.assertEqual(api_resp.status_code, 200)
        data = api_resp.get_json()
        self.assertIn('access_token', data)

    def test_03_normal_user_can_login(self):
        """Verify that normal user (like nagasairamesh143@gmail.com) can log in and is routed to dashboard."""
        # Ensure a test normal user exists
        test_email = 'norm_test_user@example.com'
        test_pwd = 'password123'
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = %s", (test_email,))
        if not c.fetchone():
            c.execute("INSERT INTO users (username, password, fullname, role) VALUES (%s, %s, %s, 'USER')",
                      (test_email, generate_password_hash(test_pwd), 'Normal User'))
            conn.commit()
        c.close()
        conn.close()

        response = self.client.post('/', data={
            'username': test_email,
            'password': test_pwd
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers.get('Location', ''))

    def test_04_users_cannot_access_admin_routes(self):
        """Verify that normal users cannot access admin-only routes."""
        test_email = 'norm_test_user@example.com'
        test_pwd = 'password123'

        # Log in as normal user
        self.client.post('/', data={
            'username': test_email,
            'password': test_pwd
        }, follow_redirects=True)

        # Attempt to access /admin
        resp_admin = self.client.get('/admin', follow_redirects=False)
        # Non-admin should be redirected away
        self.assertEqual(resp_admin.status_code, 302)
        self.assertIn('/ui_predict', resp_admin.headers.get('Location', ''))

        # Attempt to access /api/admin with user JWT
        login_resp = self.client.post('/api/login', json={
            'username': test_email,
            'password': test_pwd
        })
        token = login_resp.get_json()['access_token']

        api_admin_resp = self.client.get('/api/admin', headers={
            'Authorization': f'Bearer {token}'
        })
        # Should be forbidden
        self.assertEqual(api_admin_resp.status_code, 403)

    def test_05_register_assigns_user_role_and_blocks_admin_username(self):
        """Verify that registration always assigns USER role and rejects admin username."""
        # 1. Attempt registering with reserved admin username
        admin_user = getattr(Config, 'ADMIN_USERNAME', 'admin')
        resp_reserved = self.client.post('/register', data={
            'username': admin_user,
            'password': 'password123',
            'confirm_password': 'password123',
            'fullname': 'Fake Admin'
        }, follow_redirects=True)
        self.assertIn(b'reserved', resp_reserved.data.lower())

        # 2. Attempt registering via API with reserved username
        api_reserved = self.client.post('/api/register', json={
            'username': admin_user,
            'password': 'password123',
            'fullname': 'Fake Admin'
        })
        self.assertEqual(api_reserved.status_code, 400)

        # 3. Register a new valid user and check assigned role in DB
        new_email = 'brand_new_person@gmail.com'
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username = %s", (new_email,))
        conn.commit()
        c.close()
        conn.close()

        api_reg = self.client.post('/api/register', json={
            'username': new_email,
            'password': 'validPassword123!',
            'fullname': 'Brand New',
            'role': 'ADMIN'  # Attempting privilege escalation
        })
        self.assertEqual(api_reg.status_code, 201)

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username = %s", (new_email,))
        row = c.fetchone()
        c.close()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row['role'], 'USER', "Registration must always assign 'USER' role")

    def test_06_idempotent_init_and_fix_admin(self):
        """Verify that restarting/re-initializing the app or running fix_admin never creates duplicate admins."""
        # Run init_db multiple times
        init_db()
        init_db()
        fix_admin()

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, role FROM users WHERE role = 'ADMIN'")
        admins = c.fetchall()
        self.assertEqual(len(admins), 1)

        # If a second admin were somehow set in the DB, init_db / fix_admin should demote it
        c.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'norm_test_user@example.com'")
        conn.commit()
        c.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'ADMIN'")
        self.assertEqual(c.fetchone()['count'], 2)

        # Run init_db or fix_admin
        init_db()

        c.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'ADMIN'")
        self.assertEqual(c.fetchone()['count'], 1)

        c.execute("SELECT role FROM users WHERE username = 'norm_test_user@example.com'")
        self.assertEqual(c.fetchone()['role'], 'USER')
        c.close()
        conn.close()

if __name__ == '__main__':
    unittest.main()
