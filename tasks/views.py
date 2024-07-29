from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import CreateTaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(req):
    return render(req, 'home.html')


def signup(req):
    if req.method == 'GET':
        return render(req, 'signup.html', {'form': UserCreationForm})
    else:
        if req.POST['password1'] == req.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=req.POST['username'], password=req.POST['password1'])
                user.save()
                # esto genera el token y lo setea en cookies (sessionid)
                login(req, user)  # crea la sesion
                return redirect('tasks')
            except IntegrityError:
                return render(req, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exists'
                })
        else:
            return render(req, 'signup.html', {
                'form': UserCreationForm,
                'error': 'Password do not match'
            })


@login_required # para que la url solo pueda ser accedida si estás Auth
def tasks(req):
    # tasks = Task.objects.all() # para traer todas
    # para traer solo las del user auth
    tasks = Task.objects.filter(user=req.user, datecompleted__isnull=True)
    return render(req, 'tasks.html', {'tasks': tasks})


@login_required
def tasksCompleted(req):
    tasks = Task.objects.filter(
        user=req.user, datecompleted__isnull=False).order_by('datecompleted')
    return render(req, 'tasks.html', {'tasks': tasks})


@login_required
def createTask(req):
    if req.method == 'GET':
        return render(req, 'createTask.html', {
            'form': CreateTaskForm
        })
    else:
        try:
            form = CreateTaskForm(req.POST)
            newTask = form.save(commit=False)
            newTask.user = req.user
            newTask.save()
            return redirect('tasks')
        except ValueError:
            return render(req, 'createTask.html', {
                'form': CreateTaskForm,
                'error': 'Please provide valid data'
            })


@login_required
def taskDetail(req, taskId):
    if req.method == 'GET':
        task = get_object_or_404(Task, pk=taskId, user=req.user)
        form = CreateTaskForm(instance=task)
        return render(req, 'taskDetail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task, pk=taskId, user=req.user)
            form = CreateTaskForm(req.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(req, 'taskDetail.html', {
                'task': task,
                'form': form,
                'error': 'Error updating Task'
            })


@login_required
def taskComplete(req, taskId):
    if req.method == 'POST':
        task = get_object_or_404(Task, pk=taskId, user=req.user)
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')


@login_required
def taskDelete(req, taskId):
    if req.method == 'POST':
        task = get_object_or_404(Task, pk=taskId, user=req.user)
        task.delete()
        return redirect('tasks')


@login_required
def signout(req):
    logout(req)
    return redirect('home')


def signin(req):
    if req.method == 'GET':
        return render(req, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        username = req.POST.get('username')
        password = req.POST.get('password')
        user = authenticate(req, username=username, password=password)
        if user is None:
            return render(req, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(req, user)
            return redirect('tasks')
