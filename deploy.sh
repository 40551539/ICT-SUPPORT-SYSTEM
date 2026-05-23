#!/bin/bash
# Quick deployment script for tickets.innbucks.org
# Run this on the server: bash deploy.sh

set -e

APP_DIR="/var/www/tickets"
DOMAIN="tickets.innbucks.org"

echo "==> Installing system dependencies..."
apt-get update -q
apt-get install -y python3 python3-pip python3-venv nginx git

echo "==> Setting up app directory..."
mkdir -p $APP_DIR
cd $APP_DIR

echo "==> Installing Python dependencies..."
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt gunicorn

echo "==> Setting up environment..."
cat > .env << 'EOF'
SECRET_KEY=cuea-ict-helpdesk-demo-key-2026-tickets-innbucks
DEBUG=False
EOF

echo "==> Running migrations and collecting static files..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "==> Creating demo admin account..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
U = get_user_model()
if not U.objects.filter(username='admin').exists():
    U.objects.create_superuser('admin', 'admin@cuea.edu', 'admin123', role='admin', first_name='Admin')
    print('Admin created: admin / admin123')
else:
    print('Admin already exists')
"

echo "==> Loading demo categories..."
python manage.py shell -c "
from tickets.models import Category
cats = ['Network', 'Hardware', 'Software', 'Email & Accounts', 'Printing', 'Other']
for name in cats:
    Category.objects.get_or_create(name=name)
print('Categories ready.')
"

echo "==> Writing systemd service..."
cat > /etc/systemd/system/tickets.service << EOF
[Unit]
Description=CUEA ICT Help Desk
After=network.target

[Service]
User=www-data
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "==> Writing nginx config..."
cat > /etc/nginx/sites-available/tickets << EOF
server {
    listen 80;
    server_name $DOMAIN 79.143.178.165;

    location /static/ {
        alias $APP_DIR/staticfiles/;
    }

    location /media/ {
        alias $APP_DIR/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

ln -sf /etc/nginx/sites-available/tickets /etc/nginx/sites-enabled/tickets
rm -f /etc/nginx/sites-enabled/default

echo "==> Starting services..."
systemctl daemon-reload
systemctl enable tickets
systemctl restart tickets
systemctl reload nginx

echo ""
echo "===================================="
echo "  DONE! Site live at http://$DOMAIN"
echo "  Admin login: admin / admin123"
echo "===================================="
