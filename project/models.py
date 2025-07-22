# Create your models here.
from users.models import CustomUser

from django.db import models
from django.utils import timezone




class Project(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('current', 'Current'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_users = models.ManyToManyField(CustomUser)

class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)