from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('EMPLOYEE', 'Employee'),
        ('MANAGER', 'Manager'),
        ('HR', 'HR'),
        ('CEO', 'CEO'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    position = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @property
    def is_manager(self):
        return self.role == 'MANAGER'
    
    @property
    def is_ceo(self):
        return self.role == 'CEO'

class Question(models.Model):
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text

class Review(models.Model):
    REVIEW_TYPES = (
        ('SELF', 'Self Review'),
        ('MANAGER', 'Manager Review'),
    )
    
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    period = models.CharField(max_length=50, default="Q1 2026")
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="1=Poor, 5=Excellent")
    
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.review_type} for {self.reviewee} by {self.reviewer}"

class ReviewResponse(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return f"Answer to {self.question} in {self.review}"
