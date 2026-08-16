import unittest
import os
import sys
import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.app import create_app
from App.config import Config

class OCRTestCase(unittest.TestCase):
    def setUp(self):
        # Configure Tesseract path if it's Windows
        if os.name == 'nt':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
        self.backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_image_path = os.path.join(self.backend_dir, "tests", "temp_test_ocr.png")
        
        # Create test image programmatically
        img = Image.new('RGB', (800, 600), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        self.test_text = "URGENT HIRING: Data Entry Clerk\nEarn $50 per hour. Weekly pay.\nWork from home."
        
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except IOError:
            font = ImageFont.load_default()
            
        d.text((50, 50), self.test_text, fill=(0, 0, 0), font=font)
        img.save(self.test_image_path)

    def tearDown(self):
        if os.path.exists(self.test_image_path):
            try:
                os.remove(self.test_image_path)
            except OSError:
                pass

    def test_ocr_extraction(self):
        # Skip test if tesseract is not found on Windows
        tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
        if os.name == 'nt' and not os.path.exists(tesseract_cmd):
            self.skipTest(f"Tesseract OCR not installed or not found at {tesseract_cmd}")
            
        img = cv2.imread(self.test_image_path)
        self.assertIsNotNone(img, "Could not read generated test image")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        extracted_text = pytesseract.image_to_string(gray).strip()
        
        self.assertTrue(len(extracted_text) > 0, "No text extracted from image")
        # Verify keywords are correctly parsed
        self.assertIn("hiring", extracted_text.lower())
        self.assertIn("entry", extracted_text.lower())
        self.assertIn("clerk", extracted_text.lower())

if __name__ == '__main__':
    unittest.main()
