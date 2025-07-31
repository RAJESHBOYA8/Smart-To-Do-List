from django.db import models
from django.contrib.auth.models import User

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return self.task