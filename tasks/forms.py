from django import forms
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'project',
            'start_date',
            'due_date',
            'priority',
            'assignee',       # ✅ correct
            'team_members',   # ✅ correct
            'progress',
            'commands',
            'status',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'commands': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assignee'].queryset = User.objects.all()
        self.fields['team_members'].queryset = User.objects.all()
