# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies that might be needed for some Python packages
# e.g., for numpy, pandas, etc.
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install Poetry
# RUN pip install poetry

# Copy only the dependency file to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code from your context to your image at /app
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run your app using uvicorn
# This will start the server and make the API available
CMD ["uvicorn", "main.api:app", "--host", "0.0.0.0", "--port", "8000"]
