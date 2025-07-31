from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_token = models.UUIDField(default=uuid.uuid4)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
