import unittest
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.app import create_app
from App.routes import get_prediction

class PredictionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_prediction_logic(self):
        with self.app.test_request_context():
            # Test text designed to trigger a Fake prediction
            fake_text = "Urgent Hiring! Data Entry Clerk needed. Work from home. Earn $500 weekly pay. No experience required. Immediate start. Contact us via Telegram."
            fake_res = get_prediction(fake_text)
            
            # Test text designed to be a Real prediction
            real_text = "We are seeking a senior software engineer with 5 years of experience in Python and PostgreSQL. Candidates should have a degree in Computer Science and strong communication skills. This is a full-time, on-site role in New York."
            real_res = get_prediction(real_text)
            
            # Assertions for fake_res structure and content
            self.assertIn("prediction", fake_res)
            self.assertIn("fake_probability", fake_res)
            self.assertIsInstance(fake_res["prediction"], str)
            self.assertIsInstance(fake_res["fake_probability"], float)
            
            # Assertions for real_res structure and content
            self.assertIn("prediction", real_res)
            self.assertIn("fake_probability", real_res)
            self.assertIsInstance(real_res["prediction"], str)
            self.assertIsInstance(real_res["fake_probability"], float)

if __name__ == '__main__':
    unittest.main()
