# tasks/utils.py

from .models import Task
from django.utils import timezone

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
