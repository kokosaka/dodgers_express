#!/bin/bash

cd /app

# Ensure logs directory exists
mkdir -p /app/logs

LOG_FILE="/app/logs/dodgers_express_$(date '+%Y-%m-%d').log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

set -a
source /app/.env
set +a

echo "[$TIMESTAMP] 🏁 Starting Dodgers Express script..." | tee -a "$LOG_FILE"

# Basic check for required environment variables
REQUIRED_VARS=("EMAIL_FROM" "EMAIL_TO" "SMTP_USER" "SMTP_PASS")

for VAR in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!VAR}" ]]; then
        echo "[$TIMESTAMP] ❌ Environment variable $VAR is not set!" | tee -a "$LOG_FILE"
        exit 1
    fi
done

# Run the script and log output
if python main.py >> "$LOG_FILE" 2>&1; then
    echo "[$TIMESTAMP] ✅ Script completed successfully." | tee -a "$LOG_FILE"
else
    echo "[$TIMESTAMP] ❌ Script failed to run." | tee -a "$LOG_FILE"
fi
