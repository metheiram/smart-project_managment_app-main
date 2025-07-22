from django import forms
from .models import Project, Comment
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']