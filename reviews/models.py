from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('EMPLOYEE', 'Employee'),
        ('MANAGER', 'Manager'),
        ('HR', 'HR'),
        ('CEO', 'CEO'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subordinates')
    position = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.username

    @property
    def is_manager(self):
        return self.role == 'MANAGER'
    
    @property
    def is_ceo(self):
        return self.role == 'CEO'

class Question(models.Model):
    text = models.CharField(max_length=500)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text

class Review(models.Model):
    REVIEW_TYPES = (
        ('SELF', 'Self Review'),
        ('MANAGER', 'Manager Review'),
        ('CEO', 'Final Review'),
    )
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    period = models.CharField(max_length=20)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True, help_text="Final comments by CEO")
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.review_type} - {self.reviewee.username} - {self.period}"

class ReviewResponse(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()

    class Meta:
        unique_together = ('review', 'question')

class ManagerFeedback(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_manager_feedback')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_manager_feedback')
    period = models.CharField(max_length=20)
    rating = models.IntegerField(help_text="Rating out of 10")
    improvements = models.TextField(help_text="What improvements do you expect from your manager?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.employee.username} to {self.manager.username}"
