#!/bin/bash
# Run this on your Oracle Cloud Instance (Ubuntu Image recommended)

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx git

echo "Creating virtual environment..."
python3 -m venv env
source env/bin/activate

echo "Installing python dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate
python manage.py collectstatic --noinput

echo "Setup complete. Please configure Gunicorn and Nginx using files in 'deployment/' folder."
