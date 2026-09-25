#!/usr/bin/env bash

set -euo pipefail

APP_DIR="/opt/omniagent"
ENV_FILE="/etc/omniagent.env"
NGINX_TEMPLATE="$APP_DIR/deploy/nginx.conf"
NGINX_FILE="/etc/nginx/sites-available/omniagent"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: run this script as root"
    exit 1
fi

echo "======================================"
echo "OmniAgent setup"
echo "======================================"

read -r -p "Domain (example: agent.example.ru): " DOMAIN

if ! [[ "$DOMAIN" =~ ^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    echo "ERROR: invalid domain"
    exit 1
fi

read -r -p "Yandex Cloud PROJECT / Folder ID: " PROJECT

if [ -z "$PROJECT" ]; then
    echo "ERROR: PROJECT cannot be empty"
    exit 1
fi

read -r -s -p "Yandex AI Studio API_KEY: " API_KEY
echo

if [ -z "$API_KEY" ]; then
    echo "ERROR: API_KEY cannot be empty"
    exit 1
fi

echo
echo "=== Creating environment file ==="

cat > "$ENV_FILE" <<ENV
PROJECT=$PROJECT
API_KEY=$API_KEY
ENV

chmod 600 "$ENV_FILE"

echo "=== Creating agent configuration ==="

CONFIG_FILE="/etc/omniagent.config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    cp "$APP_DIR/config/agent.example.json" "$CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"
    echo "Created $CONFIG_FILE"
else
    echo "$CONFIG_FILE already exists - keeping current configuration"
fi

unset API_KEY

echo "=== Configuring nginx ==="

cp "$NGINX_TEMPLATE" "$NGINX_FILE"

sed -i "s/YOUR_DOMAIN/$DOMAIN/g" "$NGINX_FILE"

ln -sf "$NGINX_FILE" /etc/nginx/sites-enabled/omniagent
rm -f /etc/nginx/sites-enabled/default

nginx -t

echo "=== Starting OmniAgent ==="

systemctl daemon-reload
systemctl enable omniagent
systemctl restart omniagent

echo "Waiting for backend..."

for i in {1..15}; do
    if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
        echo "Backend is healthy"
        break
    fi

    if [ "$i" -eq 15 ]; then
        echo "ERROR: OmniAgent did not start"
        echo
        systemctl status omniagent --no-pager || true
        exit 1
    fi

    sleep 1
done

echo "=== Reloading nginx ==="

systemctl reload nginx

echo "=== Checking DNS ==="

getent hosts "$DOMAIN" || {
    echo
    echo "ERROR: domain does not resolve yet."
    echo "Create an A record pointing $DOMAIN to this VPS."
    echo "Then run setup.sh again."
    exit 1
}

echo "=== Enabling HTTPS ==="

certbot \
    --nginx \
    -d "$DOMAIN" \
    --non-interactive \
    --agree-tos \
    --redirect \
    --register-unsafely-without-email

echo "=== Final check ==="

curl -fsS "https://$DOMAIN/health"

echo
echo
echo "======================================"
echo "OmniAgent deployed successfully"
echo
echo "Agent:"
echo "https://$DOMAIN/static/widget-app.html"
echo
echo "Widget:"
echo "https://$DOMAIN/static/widget.js"
echo
echo "Health:"
echo "https://$DOMAIN/health"
echo "======================================"
