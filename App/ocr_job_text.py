import cv2
import pytesseract
from PIL import Image

# Path to image
image_path = "job_poster.jpg"  # sample image

# Read image
img = cv2.imread(image_path)

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Extract text
text = pytesseract.image_to_string(gray)

print("Extracted Text:")
print(text)
