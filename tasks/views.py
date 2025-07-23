from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .decorators import is_project_manager_or_admin

@login_required
def task_list(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    tasks = Task.objects.all()

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(project__name__icontains=query) |
            Q(assignee__username__icontains=query)
        )

    if status_filter and status_filter != 'all':
        tasks = tasks.filter(status=status_filter)

    context = {
        'tasks': tasks,
        'query': query,
        'status_filter': status_filter,
    }

    return render(request, 'tasks/TaskTab.html', context)



@login_required
@is_project_manager_or_admin
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Task created successfully!")
            return redirect('tasks:tasks_tab')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_create.html', {'form': form})


@login_required
@is_project_manager_or_admin
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('tasks:tasks_tab')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_edit.html', {'form': form})

@login_required
def tasks_tab(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    tasks = Task.objects.all()

    # ✅ Auto update each task's status before showing
    for task in tasks:
        task.auto_update_status()

    # Apply search filter
    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(project__name__icontains=query) |
            Q(assignee__username__icontains=query)
        )

    # Apply status filter
    if status_filter and status_filter != 'all':
        tasks = tasks.filter(status=status_filter)

    context = {
        'tasks': tasks,
        'query': query,
        'status_filter': status_filter,
    }

    return render(request, 'tasks/tasks_tab.html', context)



@login_required
@is_project_manager_or_admin
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    messages.success(request, "Task deleted successfully!")
    return redirect('tasks:tasks_tab')

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required

def mark_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Update the status and progress
    task.progress = 100
    task.status = 'completed'
    task.save()

    # Redirect back to task detail or task list
    return redirect('tasks:task_detail', pk=task_id)