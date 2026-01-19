#!/bin/bash
# AWS Ubuntu Deployment Script for Performance Review App
# Run this script on your AWS EC2 Ubuntu instance

set -e  # Exit on error

echo "=== Performance Review App - AWS Deployment Script ==="

# Variables
APP_DIR="/home/ubuntu/performance_review"
VENV_DIR="$APP_DIR/venv"

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx

# Create app directory
echo "Setting up application directory..."
mkdir -p $APP_DIR
mkdir -p $APP_DIR/logs

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv $VENV_DIR

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r $APP_DIR/requirements_prod.txt

# Set up environment file
if [ ! -f "$APP_DIR/.env" ]; then
    echo "Creating .env file from template..."
    cp $APP_DIR/.env.example $APP_DIR/.env
    # Generate a random secret key
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
    sed -i "s/your-super-secret-key-generate-a-new-one/$SECRET_KEY/" $APP_DIR/.env
    echo "IMPORTANT: Update .env with your domain/IP!"
fi

# Collect static files
echo "Collecting static files..."
export DJANGO_SETTINGS_MODULE=performance_review.settings_prod
python $APP_DIR/manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python $APP_DIR/manage.py migrate

# Set up Gunicorn service
echo "Setting up Gunicorn service..."
sudo cp $APP_DIR/deployment/gunicorn.service /etc/systemd/system/performance_review.service
sudo systemctl daemon-reload
sudo systemctl enable performance_review
sudo systemctl start performance_review

# Set up Nginx
echo "Setting up Nginx..."
sudo cp $APP_DIR/deployment/nginx_site.conf /etc/nginx/sites-available/performance_review
sudo ln -sf /etc/nginx/sites-available/performance_review /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Set permissions
echo "Setting permissions..."
sudo chown -R ubuntu:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Next steps:"
echo "1. Update /home/ubuntu/performance_review/.env with your domain/IP"
echo "2. Update deployment/nginx_site.conf with your domain/IP"
echo "3. Restart services: sudo systemctl restart performance_review nginx"
echo "4. Create superuser: python manage.py createsuperuser"
echo ""
echo "Your app should be available at: http://your-server-ip/"
