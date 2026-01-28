FROM python:3.9-slim

# Install system dependencies (Tesseract + OpenCV deps)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables (Set these in your dashboard also)
ENV FLASK_APP=App.app
ENV FLASK_ENV=production

EXPOSE 5000

# Use Gunicorn to serve the app
CMD ["gunicorn", "App.app:create_app()", "--bind", "0.0.0.0:5000"]
