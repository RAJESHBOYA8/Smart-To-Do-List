import datetime
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Todo
from .forms import TodoForm
from base.models import Profile, Note
from base.emails import account_activation_email
import json

@login_required
def home(request):
    selected_date = request.GET.get('date')
    todos = Todo.objects.filter(user=request.user)
    if selected_date:
        todos = todos.filter(due_date=selected_date)
    total = todos.count()
    completed = todos.filter(status='Completed').count()
    pending = todos.filter(status='Pending').count()
    overdue_tasks = todos.filter(due_date__lt=datetime.date.today(), status__in=['Pending'])
    overdue = overdue_tasks.count()
    completed_tasks = todos.filter(status='Completed')
    pending_tasks = todos.filter(status='Pending')
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:5]
    return render(request, 'dashboard.html', {
        'total': total,
        'completed': completed,
        'pending': pending,
        'overdue': overdue,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'all_tasks': todos,
        'notes': notes,
        'selected_date': selected_date,
        'today': datetime.date.today(),
    })
@login_required
def notes_view(request):
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'notes.html', {'notes': notes})

@login_required
@require_http_methods(["GET", "POST"])
def add_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Note.objects.create(user=request.user, title=title, content=content)
        return redirect('notes')
    return render(request, 'add_note.html')

@login_required
@require_http_methods(["GET", "POST"])
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        note.title = request.POST.get('title')
        note.content = request.POST.get('content')
        note.save()
        return redirect('notes')
    return render(request, 'edit_note.html', {'note': note})

@login_required
@require_http_methods(["POST"])
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.delete()
    return redirect('notes')




@login_required
def edit_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)

    if request.method == "POST":
        task = request.POST.get("task")
        priority = request.POST.get("priority")
        todo.task = task
        todo.priority = priority
        todo.save()
        return redirect("todo")

    return render(request, "edit_todo.html", {"todo": todo})

def edit_task(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'edit_task.html', {'form': form, 'todo': todo})



@login_required
def complete_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.status = 'Completed'
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.delete()
    return redirect('todo')



@login_required
def todo_view(request):
    if request.method == "POST":
        task = request.POST.get("task")
        priority = request.POST.get("priority")
        Todo.objects.create(
            user=request.user,
            task=task,
            priority=priority
        )
        return redirect("todo")

    todos = Todo.objects.filter(user=request.user)
    return render(request, "todoapp.html", {"todos": todos})


def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = 'Invalid username or password.'

    return render(request, 'login.html', {'error': error})

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def password_reset_request(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        users = []
        if '@' in identifier:
            users = User.objects.filter(email=identifier)
        else:
            try:
                user = User.objects.get(username=identifier)
                users = [user]
            except User.DoesNotExist:
                users = []

        if users:
            for user in users:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                try:
                    send_mail(
                        'Password Reset Request',
                        f'Hi {user.username}, click the link below to reset your password:\n{reset_link}',
                        'noreply@yourdomain.com',
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"Error sending password reset email to {user.email}: {e}")
                    messages.error(request, f'Error sending password reset email to {user.email}. Please try again later.')
                    return redirect('password_reset_request')
            messages.success(request, 'Password reset email sent. Please check your inbox.')
            return redirect('login')
        else:
            messages.error(request, 'User not found with that username or email.')

    return render(request, 'password_reset_request.html')

def password_reset_confirm(request, uidb64, token):
    UserModel = User
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            logger.debug(f"Password reset attempt: new_password={new_password}, confirm_password={confirm_password}")
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                logger.debug("Password reset successful and saved to DB.")
                messages.success(request, 'Password has been reset successfully. You can now log in.')
                return redirect('login')
            else:
                logger.debug("Password reset failed: passwords do not match.")
                messages.error(request, 'Passwords do not match.')
        return render(request, 'password_reset_form.html', {'validlink': True})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return render(request, 'password_reset_form.html', {'validlink': False})




def activation_email(request, username):
    try:
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been verified successfully. Please login.')
        return redirect('login')
    except User.DoesNotExist:
        messages.error(request, 'Activation failed. User not found.')
        return redirect('register')


def activate_account(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('login')
    else:
        return render(request, 'activation_failed.html')


def register_view(request):
    message = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            message = 'Username already exists.'
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False
            )
            
            # Create profile for the user
            Profile.objects.create(user=user)

            # Send verification email
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = request.build_absolute_uri(
                reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
            )

            send_mail(
                subject='Activate your account',
                message=f'Hi {first_name}, click the link to verify your account: {activation_link}',
                from_email='noreply@yourdomain.com',
                recipient_list=[email],
                fail_silently=False,
            )

            message = 'Registration successful. A verification email has been sent.'

    return render(request, 'register.html', {'message': message})

@login_required
def mark_done(request, task_id):
    task = get_object_or_404(Todo, id=task_id, user=request.user)
    if request.method == 'POST':
        task.status = 'Completed'
        task.save()
    return redirect('todo')
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Todo, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
    return redirect('todo')