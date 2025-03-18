FROM python:3.13-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements.txt first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the Flask application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]