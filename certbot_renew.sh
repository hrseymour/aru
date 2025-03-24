#!/bin/bash

echo "Starting Let's Encrypt renewal process: $(date)" >> /home/ubuntu/repos/aru/certbot_renew.log

sudo systemctl stop nginx
sudo certbot renew >> /home/ubuntu/repos/aru/certbot_renew.log 2>&1
sudo systemctl start nginx

sudo certbot certificates >> /home/ubuntu/repos/aru/certbot_renew.log 2>&1

echo "Renewal process completed: $(date)" >> /home/ubuntu/repos/aru/certbot_renew.log
