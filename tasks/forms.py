# tasks/forms.py

from django import forms
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'start_date', 'due_date', 'priority', 'assignee', 'assigned_users', 'progress', 'commands']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'assigned_users': forms.SelectMultiple(attrs={'class': 'bg-gray-800 text-white'}),
            'commands': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['assigned_users'].queryset = User.objects.all()
        self.fields['assignee'].queryset = User.objects.all()
