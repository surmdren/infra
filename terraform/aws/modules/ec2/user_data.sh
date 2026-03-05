#!/bin/bash

# Disable ufw (we use AWS Security Groups instead)
ufw disable || true
ufw --force reset || true

# Ubuntu 22.04 uses ssh.socket (socket activation) which can cause issues
# Switch to traditional sshd daemon mode
systemctl disable ssh.socket 2>/dev/null || true
systemctl stop ssh.socket 2>/dev/null || true
systemctl enable ssh
systemctl restart ssh

# Install Nginx
apt-get update -y
apt-get install -y nginx git curl wget unzip htop

# Enable & start Nginx
systemctl enable nginx
systemctl start nginx

# Default Nginx config
cat > /etc/nginx/sites-available/default <<'NGINXEOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    root /var/www/html;
    index index.html;
    server_name _;
    location / {
        try_files $uri $uri/ =404;
    }
}
NGINXEOF

nginx -t && systemctl reload nginx

echo "Bootstrap complete" >> /var/log/user-data.log
