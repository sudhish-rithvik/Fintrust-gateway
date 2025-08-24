# Base image: lightweight Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install OS dependencies for TenSEAL and cryptography
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask service
CMD ["python", "app.py"]
