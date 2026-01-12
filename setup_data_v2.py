import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance_review.settings')
django.setup()

from reviews.models import User, Question

# 1. Create Questions
q1, c = Question.objects.get_or_create(text="What were your main achievements this quarter?", defaults={'order': 1})
q2, c = Question.objects.get_or_create(text="What challenges did you encounter?", defaults={'order': 2})
q3, c = Question.objects.get_or_create(text="What are your goals for the next quarter?", defaults={'order': 3})
print("Questions created.")

# 2. Create Users
if not User.objects.filter(username='ceo').exists():
    ceo = User.objects.create_user(username='ceo', password='password', role='CEO', email='ceo@company.com')
    print("Created CEO")
else:
    ceo = User.objects.get(username='ceo')

if not User.objects.filter(username='manager').exists():
    manager = User.objects.create_user(username='manager', password='password', role='MANAGER', position='Engineering Manager', email='manager@company.com')
    manager.manager = ceo
    manager.save()
    print("Created Manager")
else:
    manager = User.objects.get(username='manager')

if not User.objects.filter(username='employee').exists():
    emp = User.objects.create_user(username='employee', password='password', role='EMPLOYEE', manager=manager, position='Software Engineer', email='dev@company.com')
    print("Created Employee")
    
# 3. Superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'password')
    print("Created Admin")

print("Setup V2 Complete.")
