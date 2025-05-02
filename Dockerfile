# Use Python base image that supports ARM (Apple Silicon)
FROM python:3.10-slim

# Set timezone
ENV TZ=America/Los_Angeles

# Create app directory
WORKDIR /app

# Copy all files
COPY requirements.txt ./
COPY main.py ./
COPY .env ./
COPY crontab.txt ./
COPY start.sh ./

# Install Python dependencies and cron
RUN apt-get update && apt-get install -y cron && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x start.sh && \
    crontab crontab.txt

# Run cron in foreground
CMD ["./start.sh"]
