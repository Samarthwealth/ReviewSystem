import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance_review.settings')
django.setup()

from reviews.models import User

# Clear existing users to avoid conflicts
if User.objects.filter(username='ceo').exists():
    print("Users already exist. Skipping creation.")
else:
    # CEO
    ceo = User.objects.create_user(username='ceo', password='password', role='CEO', email='ceo@company.com')
    print("Created CEO")

    # Manager
    manager = User.objects.create_user(username='manager', password='password', role='MANAGER', position='Engineering Manager', email='manager@company.com')
    manager.manager = ceo
    manager.save()
    print("Created Manager")

    # Employee
    emp = User.objects.create_user(username='employee', password='password', role='EMPLOYEE', manager=manager, position='Software Engineer', email='dev@company.com')
    print("Created Employee")

    print("Setup Complete.")
    print("Credentials: ceo/password, manager/password, employee/password")
