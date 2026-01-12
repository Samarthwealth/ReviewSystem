import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance_review.settings')
django.setup()

from reviews.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'password')
    print("Superuser 'admin' created.")
else:
    print("Superuser 'admin' already exists.")
