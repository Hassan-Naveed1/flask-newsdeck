# Simple dev container; for production swap to gunicorn as needed.
FROM python:3.12-slim

# Prevent Python from writing .pyc and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first (better build caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Default Flask envs (can be overridden at run)
ENV FLASK_APP=app
ENV FLASK_ENV=development
EXPOSE 5000

# Note: supply NEWSAPI_KEY at runtime: -e NEWSAPI_KEY=xxx
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]
