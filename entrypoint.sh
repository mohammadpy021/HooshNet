#!/bin/bash

# Function to wait for MySQL
wait_for_mysql() {
    echo "Waiting for MySQL..."
    while ! mysqladmin ping -h"$MYSQL_HOST" --silent; do
        sleep 1
    done
    echo "MySQL is up - executing command"
}

# Wait for database
# We need to install mysql-client in Dockerfile to use mysqladmin, or use python to check
# For simplicity, let's use a python one-liner or just sleep a bit if mysql-client is not there.
# But I added default-libmysqlclient-dev and I should add mariadb-client or default-mysql-client to Dockerfile for this tool.
# Let's use a python script to check connection to be safe and dependency-free (since we have python).

echo "Waiting for Database..."
python3 -c "
import time
import mysql.connector
from mysql.connector import Error

while True:
    try:
        conn = mysql.connector.connect(
            host='$MYSQL_HOST',
            user='$MYSQL_USER',
            password='$MYSQL_PASSWORD',
            port=$MYSQL_PORT
        )
        if conn.is_connected():
            print('Database connected!')
            conn.close()
            break
    except Error as e:
        print(f'Waiting for database: {e}')
        time.sleep(2)
"

# Run Migrations
echo "Running Database Migrations..."
# Force Rebuild 2024-12-29
python3 -c "from professional_database import ProfessionalDatabaseManager; db = ProfessionalDatabaseManager(); db.init_database()"

# Fallback: Install dependencies if missing (in case image wasn't rebuilt)
if ! command -v openssl &> /dev/null; then
    echo "Installing missing dependencies..."
    apt-get update && apt-get install -y openssl certbot
fi

# Ensure SSL Directory Exists
mkdir -p /etc/nginx/ssl

# Check for Let's Encrypt certificates on host (mounted from /etc/letsencrypt)
LETSENCRYPT_CERT=""
if [ -d /etc/letsencrypt/live ]; then
    # Find the first domain directory
    for domain_dir in /etc/letsencrypt/live/*/; do
        if [ -f "${domain_dir}fullchain.pem" ] && [ -f "${domain_dir}privkey.pem" ]; then
            echo "Found Let's Encrypt certificate in ${domain_dir}"
            ln -sf "${domain_dir}fullchain.pem" /etc/nginx/ssl/fullchain.pem
            ln -sf "${domain_dir}privkey.pem" /etc/nginx/ssl/privkey.pem
            LETSENCRYPT_CERT="yes"
            break
        fi
    done
fi

# Generate Self-Signed Certificate if no Let's Encrypt cert found
if [ ! -f /etc/nginx/ssl/fullchain.pem ] || [ ! -f /etc/nginx/ssl/privkey.pem ]; then
    echo "Generating self-signed certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/privkey.pem \
        -out /etc/nginx/ssl/fullchain.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Write Nginx config directly (FOOLPROOF - no file dependencies)
echo "Writing Nginx configuration..."
cat > /etc/nginx/sites-available/vpn_bot << 'NGINX_CONFIG'
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_CONFIG

# Ensure symlink exists and default is removed
ln -sf /etc/nginx/sites-available/vpn_bot /etc/nginx/sites-enabled/vpn_bot
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "Testing Nginx configuration..."
if nginx -t; then
    echo "Nginx configuration is valid!"
else
    echo "ERROR: Nginx configuration test failed!"
    cat /etc/nginx/sites-available/vpn_bot
fi

# Start Supervisor
echo "Starting Supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
