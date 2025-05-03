# Use Python 3.12 base image (slim, ARM-compatible)
FROM python:3.12-slim

# Set timezone
ENV TZ=America/Los_Angeles

# Create working directory
WORKDIR /app

# Copy all files
COPY requirements.txt ./
COPY main.py ./
COPY .env ./
COPY crontab.txt ./
COPY start.sh ./
COPY templates/ ./templates/

# Install cron and dependencies
RUN apt-get update && apt-get install -y cron && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x start.sh && \
    mkdir -p /app/logs && \
    crontab crontab.txt

# Run the cron scheduler and our script
# Copy crontab and install it
RUN crontab crontab.txt

# Start cron in foreground
CMD ["cron", "-f"]

