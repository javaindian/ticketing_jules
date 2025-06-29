# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies required for psycopg2 and potentially other packages
# gcc and libpq-dev are common for PostgreSQL client compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code into the container
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8000

# Define the command to run your app using Gunicorn for a more production-like setup
# For development, you might use: CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# Ensure Gunicorn is in your requirements.txt if you use it here.
# For now, sticking to runserver for simplicity as Gunicorn wasn't explicitly added to requirements.
# Add "gunicorn" to requirements.txt if this is uncommented:
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "library_system.wsgi:application"]

# Command to run the development server (ensure migrations are run as part of startup in docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
