#!/bin/bash

# Variables for time intervals (in minutes)
CHECK_INTERVAL=10
MAX_AGE=30

# Directory to clean
# TEMP_DIR="/home/ubuntu/repos/aru/data/processed"
TEMP_DIR="/home/harlan/repos/aru/data/processed"

# Find and delete files older than MAX_AGE minutes
find "$TEMP_DIR" -type f -mmin +$MAX_AGE -delete

# Log the cleanup (optional)
echo "$(date): Cleaned files older than $MAX_AGE minutes from $TEMP_DIR" >> /var/log/temp_cleanup.log