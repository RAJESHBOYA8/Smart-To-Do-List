from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from base import emails
from base.emails import account_activation_email
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Todo
from django.views.decorators.http import require_http_methods
from .forms import TodoForm

@login_required
def home(request):
    todos = Todo.objects.filter(user=request.user)
    total = todos.count()
    completed = todos.filter(status='Completed').count()
    pending = todos.filter(status='Pending').count()
    overdue = todos.filter(status='Overdue').count()
    return render(request, 'dashboard.html', {
        'total': total,
        'completed': completed,
        'pending': pending,
        'overdue': overdue,
    })




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
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
            # Changed to dashboard
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
    return render(request, 'login.html')




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
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True
                )
                profile = Profile.objects.get(user=user)
                account_activation_email(email=user.email, email_token=str(profile.email_token))
                message = 'Registration successful. A verification email has been sent.'

    return render(request, 'register.html', {'message': message})

def logout_view(request):
    logout(request)
    return redirect('login')
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