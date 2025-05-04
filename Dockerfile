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
COPY static/ ./static/

# Install cron and dependencies
RUN apt-get update && apt-get install -y cron && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x start.sh && \
    mkdir -p /app/logs && \
    crontab crontab.txt

# Set the time zone to your desired time zone (e.g., America/Los_Angeles)
RUN apt-get update && apt-get install -y tzdata \
    && cp /usr/share/zoneinfo/America/Los_Angeles /etc/localtime \
    && echo "America/Los_Angeles" > /etc/timezone 

# Run the cron scheduler and our script
# Copy crontab and install it
RUN crontab crontab.txt

# Start cron in foreground
CMD ["cron", "-f"]

