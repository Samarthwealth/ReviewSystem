#!/bin/bash

# Deployment Script
# Usage: ./deploy.sh

echo "Starting deployment..."

# 1. Pull latest code
echo "Pulling latest code from GitHub..."
git pull origin main

# 2. Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 3. Apply Migrations
echo "Applying database migrations..."
python manage.py migrate

# 4. Collect Static Files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "------------------------------------------------"
echo "Deployment steps completed successfully."
echo "NOTE: If you are using Gunicorn/Systemd, please restart the service:"
echo "sudo systemctl restart gunicorn"
echo "------------------------------------------------"
