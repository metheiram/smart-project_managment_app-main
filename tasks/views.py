from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .decorators import is_project_manager_or_admin
from project.ai_utils import assign_tasks, generate_subtasks
import logging
from project.ai_utils import get_best_user_for_task
from project.decorators import is_project_manager_or_admin  
from project.ai_utils import get_best_user_for_task
from django.utils.dateparse import parse_date
from django.http import JsonResponse 
logger = logging.getLogger(__name__)

@login_required
def task_list(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    tasks = Task.objects.all()

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(project__title__icontains=query) |
            Q(assignee__username__icontains=query)
        ).distinct()

    if status_filter and status_filter != 'all':
        tasks = tasks.filter(status=status_filter)

    context = {
        'tasks': tasks,
        'query': query,
        'status_filter': status_filter or 'all',
    }

    return render(request, 'tasks/TaskTab.html', context)
@login_required
@is_project_manager_or_admin
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            project = task.project

            # Debug project
            print("📌 Project selected:", project)
            print("📌 Project start:", project.start_date, "end:", project.end_date)
            print("🧪 Final Task Info:")
            print("Title:", task.title)
            print("Due date:", task.due_date)
            print("Assignee:", task.assignee)

            # Set due_date
            if not task.due_date and project.start_date and project.end_date:
                duration = (project.end_date - project.start_date).days
                print("📌 Duration in days:", duration)
                if duration > 0:
                    offset_days = int(duration * 0.75)
                    due_datetime = timezone.datetime.combine(
                        project.start_date, timezone.datetime.min.time()
                    ) + timezone.timedelta(days=offset_days)
                    task.due_date = timezone.make_aware(due_datetime)
                    print("✅ Auto-set due_date:", task.due_date)
                else:
                    print("❌ Invalid project duration")

            # AI Assignee
            if not task.assignee:
                try:
                    best_user = get_best_user_for_task(task.title)
                    print("✅ AI selected user:", best_user)
                    if best_user:
                        task.assignee = best_user
                except Exception as e:
                    print("❌ AI error:", str(e))

            print("📝 Final task before save:")
            print("Title:", task.title)
            print("Due date:", task.due_date)
            print("Assignee:", task.assignee)

            task.save()
            form.save_m2m()
            messages.success(request, f"Task created! Assigned to {task.assignee.username if task.assignee else 'No one'}")
            return redirect('tasks:tasks_tab')
        else:
            print("❌ Form errors:", form.errors)
            messages.error(request, "Please correct the errors in the form.")
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
            messages.error(request, "Form validation failed. Please correct the errors.")
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_edit.html', {'form': form, 'task': task})

@login_required
def tasks_tab(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    tasks = Task.objects.all()
    logger.info(f"Retrieved {tasks.count()} tasks before filtering")

    for task in tasks:
        task.auto_update_status()

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(project__title__icontains=query) |
            Q(assignee__username__icontains=query)

        ).distinct()
        logger.info(f"After search query '{query}', {tasks.count()} tasks remain")

    if status_filter and status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
        logger.info(f"After status filter '{status_filter}', {tasks.count()} tasks remain")

    context = {
        'tasks': tasks,
        'query': query,
        'status_filter': status_filter or 'all',
    }

    logger.info(f"Final tasks sent to template: {tasks.count()}")
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
    task.progress = 100
    task.status = 'completed'
    task.save()
    return redirect('tasks:task_detail', pk=task_id)

@login_required
def tasks_by_date(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)

    try:
        date = parse_date(date_str)
        tasks = Task.objects.filter(due_date=date)
        # tasks = Task.objects.filter(due_date__date=date)
        task_data = [
            {
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'project': task.project.title if task.project else "No Project",
            }
            for task in tasks
        ]
        return JsonResponse({'tasks': task_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
