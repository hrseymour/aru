#!/bin/bash

# ========== SETUP INSTRUCTIONS ==========
# To set up this script and cron job:
#
# 1. Make the script executable:
#    sudo chmod +x /usr/local/bin/cleanup_temp.sh
#
# 2. Test the script (optional):
#    sudo /usr/local/bin/cleanup_temp.sh
#
# 3. Create a Cron job:
#    sudo crontab -e
#
# 4. Add the following line to run the script every 10 minutes:
#    */10 * * * * /usr/local/bin/cleanup_temp.sh
#
# 5. Verify the Cron job is set up:
#    sudo crontab -l
#
# 6. Set proper permissions for your temp directory:
#    sudo chmod 770 /path/to/your/temp/directory
#
# =========================================

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