import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')
django.setup()

from django.contrib.auth.models import User

def reset_password(username, new_password):
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        print(f"Password for user '{username}' has been reset.")
    except User.DoesNotExist:
        print(f"User '{username}' does not exist.")

if __name__ == "__main__":
    reset_password('rajeshboya8', '1234')
