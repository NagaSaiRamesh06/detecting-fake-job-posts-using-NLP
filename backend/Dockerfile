FROM python:3.9-slim

# Install system dependencies including Tesseract OCR and OpenCV requirements
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code
COPY . .

# Run the app with gunicorn
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000"]
