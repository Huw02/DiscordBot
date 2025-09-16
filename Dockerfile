FROM python:3.11-slim

WORKDIR /app

# Installer Chromium + Chromedriver
RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    wget unzip gnupg curl \
    && rm -rf /var/lib/apt/lists/*

# Installer Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
