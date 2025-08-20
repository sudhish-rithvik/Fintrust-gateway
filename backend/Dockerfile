# Use official Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app
ENV PYTHONPATH=/app

# Copy dependency list and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app /app
# Copy the entire backend app code
COPY audit-log /app/audit_log



# COPY ../audit-log /audit_log

# Expose port (FastAPI runs on 8000)
EXPOSE 8000

# Start FastAPI server using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
