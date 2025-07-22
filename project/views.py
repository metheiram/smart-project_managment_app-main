

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Comment
from .forms import ProjectForm, CommentForm, CustomUserCreationForm
from .decorators import is_project_manager_or_admin
from django.contrib.auth import authenticate, login

@login_required
def dashboard(request):
    if request.user.role in ['admin', 'manager']:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(assigned_users=request.user)
    return render(request, 'data/dashboard.html', {'projects': projects})

@login_required
def project_list(request):
    return render(request, 'project/project_tab.html', {'projects': Project.objects.all()})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    comments = Comment.objects.filter(project=project)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = CommentForm()
    return render(request, 'project/project_detail.html', {'project': project, 'comments': comments, 'form': form})

@login_required
@is_project_manager_or_admin
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'project/project_form.html', {'form': form})

@login_required
@is_project_manager_or_admin
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect('project_detail', pk=pk)
    return render(request, 'project/project_form.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'project/register.html', {'form': form})