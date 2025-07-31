from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Todo
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('todo')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def todo_view(request):
    if request.method == 'POST':
        task = request.POST.get('task')
        priority = request.POST.get('priority')
        Todo.objects.create(user=request.user, task=task, priority=priority)
        messages.success(request, "Task added successfully!")

    tasks = Todo.objects.filter(user=request.user)
    return render(request, 'todoapp.html', {'tasks': tasks})

@login_required
def mark_done(request, task_id):
    task = Todo.objects.get(id=task_id, user=request.user)
    task.status = "Done"
    task.save()
    return redirect('todo')

@login_required
def delete_task(request, task_id):
    task = Todo.objects.get(id=task_id, user=request.user)
    task.delete()
    return redirect('todo')
