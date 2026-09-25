#!/usr/bin/env bash

set -e

APP_DIR="/opt/omniagent"
SERVICE_FILE="/etc/systemd/system/omniagent.service"
NGINX_FILE="/etc/nginx/sites-available/omniagent"
ENV_FILE="/etc/omniagent.env"

echo "=== Updating packages ==="
apt update

echo "=== Installing system packages ==="
apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    curl \
    nginx \
    certbot \
    python3-certbot-nginx

echo "=== Creating Python environment ==="
cd "$APP_DIR"

python3 -m venv .venv

source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "=== Installing systemd service ==="
cp "$APP_DIR/deploy/omniagent.service" "$SERVICE_FILE"

systemctl daemon-reload
systemctl enable omniagent

echo "=== Installing nginx config ==="
cp "$APP_DIR/deploy/nginx.conf" "$NGINX_FILE"

ln -sf "$NGINX_FILE" /etc/nginx/sites-enabled/omniagent
rm -f /etc/nginx/sites-enabled/default

nginx -t

echo
echo "======================================"
echo "Base installation completed."
echo
echo "Next steps:"
echo "1. Create $ENV_FILE"
echo "2. Replace YOUR_DOMAIN in:"
echo "   $NGINX_FILE"
echo "3. Start:"
echo "   systemctl start omniagent"
echo "4. Reload nginx:"
echo "   systemctl reload nginx"
echo "5. Enable HTTPS:"
echo "   certbot --nginx -d YOUR_DOMAIN"
echo "======================================"
