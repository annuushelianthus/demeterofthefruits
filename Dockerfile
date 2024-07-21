FROM python:3.9-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt /tmp/
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu \
    && rm /tmp/requirements.txt

# Create and set working directory
WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser --uid 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
