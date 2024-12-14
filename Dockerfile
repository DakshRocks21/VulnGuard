# syntax=docker/dockerfile:1

# Use a specific Python version as the base image
ARG PYTHON_VERSION=3.12.8
FROM python:${PYTHON_VERSION}-slim as base

# Prevent Python from writing pyc files and enable unbuffered output for logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies
# Use requirements.txt for installing Python dependencies
COPY requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy the source code into the container
COPY . /app

# Debugging: Ensure files are copied correctly
RUN echo "Contents of /app:" && ls -la /app

# Verify the current working directory
RUN echo "Current working directory:" && pwd

# Run the application
CMD ["python", "/app/main.py"]
