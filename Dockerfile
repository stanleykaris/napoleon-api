# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /code/

# Make the entrypoint script executable
RUN chmod +x /code/docker-entrypoint.sh

# Create and set permissions for media and static directories
RUN mkdir -p /code/media /code/staticfiles \
    && chmod -R 755 /code/media /code/staticfiles

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' myuser \
    && chown -R myuser:myuser /code
USER myuser

# Set the entrypoint
ENTRYPOINT ["/code/docker-entrypoint.sh"]

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
