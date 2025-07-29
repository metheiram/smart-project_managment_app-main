# tasks/utils.py

from .models import Task
from django.utils import timezone
from django.contrib.auth import get_user_model
def update_overdue_tasks():
    """Mark tasks as overdue if past due date and not complete"""
    tasks = Task.objects.filter(due_date__lt=timezone.now()).exclude(status='completed')
    for task in tasks:
        task.status = 'overdue'
        task.save()

def auto_complete_tasks():
    """Mark tasks as completed if progress is 100%"""
    tasks = Task.objects.filter(progress=100).exclude(status='completed')
    for task in tasks:
        task.status = 'completed'
        task.save()
from django.contrib.auth import get_user_model
User = get_user_model()

def get_best_user_for_task(task_title):
    # This is just a placeholder. Replace with real AI logic.
    return User.objects.filter(is_active=True).order_by('?').first()
