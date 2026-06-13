FROM python:3.13-slim

# Install system dependencies for OpenCV and build tools for dlib
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libxkbcommon0 \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run migrations and start gunicorn
CMD python manage.py migrate && gunicorn --bind 0.0.0.0:${PORT:-8000} rakshnetra.wsgi:application
