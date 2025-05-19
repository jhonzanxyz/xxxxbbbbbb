# Use the official Alpine-based Python image from the Docker Hub
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install necessary packages for running Gunicorn and your app
RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev bash

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Command to run both Gunicorn and your bot script
CMD gunicorn --bind 0.0.0.0:8000 app:app & python3 m.py
