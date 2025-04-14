FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code
COPY . .

# Make init script executable
RUN chmod +x init.sh

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application with Gunicorn
CMD ["sh", "/app/init.sh"]