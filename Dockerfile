FROM python:3.10-slim

# Avoid interactive prompts
ARG DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project files
COPY . .

EXPOSE 8501

# Run your script
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
