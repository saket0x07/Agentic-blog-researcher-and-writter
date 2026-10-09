# Base Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (curl for healthchecks, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY config.py .
COPY app.py .
COPY api.py .
COPY blog_agent/ ./blog_agent/

# Ensure output directory exists for blog drafts and images
RUN mkdir -p /app/output/images

# Expose Streamlit port (8501) and FastAPI port (8000)
EXPOSE 8501 8000

# Default command: launch the Streamlit Web Application
# (Can be overridden at runtime to run FastAPI via: uvicorn api:app --host 0.0.0.0 --port 8000)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
