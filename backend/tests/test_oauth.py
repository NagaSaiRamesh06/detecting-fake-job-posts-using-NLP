import unittest
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.app import create_app
from App.config import Config
from App.database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class AuthAndSocialRemovalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    @classmethod
    def tearDownClass(cls):
        # Clean up any test users created during auth tests
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE username IN (%s, %s, %s)", 
                      ('test_user_auth@example.com', 'new_reg_user@company.org', 'brand_new_person@gmail.com'))
            conn.commit()
            c.close()
            conn.close()
        except Exception:
            pass

    def test_01_social_buttons_and_divider_completely_removed(self):
        """Verify Google and GitHub login buttons, icons, and divider are completely removed from login page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Social elements must NOT be present
        self.assertNotIn('Sign in with Gmail', html)
        self.assertNotIn('Sign in with Google', html)
        self.assertNotIn('Sign in with GitHub', html)
        self.assertNotIn('btn-google-login', html)
        self.assertNotIn('btn-github-login', html)
        self.assertNotIn('OR CONTINUE WITH', html)
        self.assertNotIn('btn-social', html)
        self.assertNotIn('social-icon', html)

        # Essential SaaS login page elements MUST be present
        self.assertIn('Welcome Back', html)
        self.assertIn('Email or Username', html)
        self.assertIn('Password', html)
        self.assertIn('Remember me', html)
        self.assertIn('Forgot Password?', html)
        self.assertIn('Sign In', html)
        self.assertIn('Create Account', html)

    def test_02_oauth_routes_completely_removed(self):
        """Verify all Google and GitHub OAuth routes have been removed and return 404."""
        oauth_endpoints = [
            '/login/google',
            '/login/github',
            '/auth/google',
            '/auth/github',
            '/auth/google/callback',
            '/auth/github/callback',
        ]
        for endpoint in oauth_endpoints:
            resp = self.client.get(endpoint)
            self.assertEqual(resp.status_code, 404, f"Endpoint {endpoint} should be removed (404)")

    def test_03_standard_user_email_password_login(self):
        """Verify standard email and password authentication works and redirects to dashboard."""
        test_email = 'test_user_auth@example.com'
        test_password = 'UserSecret123!'
        
        # Seed test user
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username = %s", (test_email,))
        c.execute("INSERT INTO users (username, password, fullname, role) VALUES (%s, %s, %s, 'USER')",
                  (test_email, generate_password_hash(test_password), 'Test User'))
        conn.commit()
        c.close()
        conn.close()

        # Perform login
        resp = self.client.post('/', data={
            'username': test_email,
            'password': test_password
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard', resp.headers.get('Location', ''))

        # Check session after follow redirects
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('username'), test_email)
            self.assertEqual(sess.get('role'), 'USER')

    def test_04_admin_password_login(self):
        """Verify admin login works and redirects to admin dashboard."""
        admin_user = getattr(Config, 'ADMIN_USERNAME', 'admin')
        admin_pass = getattr(Config, 'ADMIN_DEFAULT_PASSWORD', 'admin')

        resp = self.client.post('/', data={
            'username': admin_user,
            'password': admin_pass
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin', resp.headers.get('Location', ''))

    def test_05_invalid_password_rejected(self):
        """Verify invalid credentials fail gracefully with flash error."""
        resp = self.client.post('/', data={
            'username': 'non_existent_user@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Invalid username or password', resp.data)

    def test_06_registration_and_login_flow(self):
        """Verify new user registration works and allows subsequent login."""
        reg_email = 'new_reg_user@company.org'
        reg_password = 'BrandNewPassword123!'
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username = %s", (reg_email,))
        conn.commit()
        c.close()
        conn.close()

        # Register new account
        resp = self.client.post('/register', data={
            'fullname': 'New User Reg',
            'username': reg_email,
            'password': reg_password,
            'confirm_password': reg_password
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)

        # Login with newly created credentials
        login_resp = self.client.post('/', data={
            'username': reg_email,
            'password': reg_password
        }, follow_redirects=False)

        self.assertEqual(login_resp.status_code, 302)
        self.assertIn('/dashboard', login_resp.headers.get('Location', ''))

    def test_07_forgot_password_page_accessible(self):
        """Verify the forgot password page remains intact and accessible."""
        resp = self.client.get('/forgot_password')
        self.assertEqual(resp.status_code, 200)

    def test_08_no_authlib_dependency(self):
        """Verify neither routes nor app import or require Authlib."""
        import App.routes as routes_module
        import App.app as app_module

        self.assertFalse(hasattr(routes_module, 'oauth'), "routes should not expose an oauth object")
        self.assertFalse(hasattr(routes_module, 'google'), "routes should not expose a google client")
        self.assertFalse(hasattr(routes_module, 'github'), "routes should not expose a github client")

    def test_09_favicon_endpoints_accessible(self):
        """Verify that favicon files return HTTP 200 via static and root routes."""
        # 1. Root /favicon.ico route
        resp_root = self.client.get('/favicon.ico')
        self.assertEqual(resp_root.status_code, 200)
        self.assertGreater(len(resp_root.data), 0)

        # 2. Static favicon.ico
        resp_ico = self.client.get('/static/favicon.ico')
        self.assertEqual(resp_ico.status_code, 200)

        # 3. Static favicon.png
        resp_png = self.client.get('/static/favicon.png')
        self.assertEqual(resp_png.status_code, 200)
        self.assertEqual(resp_png.mimetype, 'image/png')

        # 4. Static favicon.svg
        resp_svg = self.client.get('/static/favicon.svg')
        self.assertEqual(resp_svg.status_code, 200)
        self.assertEqual(resp_svg.mimetype, 'image/svg+xml')

    def test_10_favicon_present_in_all_pages(self):
        """Verify that favicon link tags are present across multiple views."""
        # Login page
        resp_login = self.client.get('/')
        self.assertEqual(resp_login.status_code, 200)
        html_login = resp_login.data.decode('utf-8')
        self.assertIn('favicon.svg', html_login)
        self.assertIn('favicon.png', html_login)
        self.assertIn('favicon.ico', html_login)

        # Registration page
        resp_reg = self.client.get('/register')
        self.assertEqual(resp_reg.status_code, 200)
        html_reg = resp_reg.data.decode('utf-8')
        self.assertIn('favicon.svg', html_reg)
        self.assertIn('favicon.png', html_reg)

        # Forgot password page
        resp_forgot = self.client.get('/forgot_password')
        self.assertEqual(resp_forgot.status_code, 200)
        html_forgot = resp_forgot.data.decode('utf-8')
        self.assertIn('favicon.svg', html_forgot)
        self.assertIn('favicon.png', html_forgot)

if __name__ == '__main__':
    unittest.main()
