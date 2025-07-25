from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from .models import Project
from .forms import ProjectForm,  CustomUserCreationForm
from .utils import update_expired_projects, update_pending_projects
from .decorators import is_project_manager_or_admin
from tasks.models import Task
from project.ai_utils import assign_tasks, generate_subtasks


@login_required
def dashboard(request):
    update_expired_projects()
    update_pending_projects()
    if request.user.role in ['admin', 'manager']:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(assigned_users=request.user)
    return render(request, 'data/dashboard.html', {'projects': projects})


@login_required
def project_list(request):
    update_expired_projects()
    update_pending_projects()
    status_filter = request.GET.get('status')
    if status_filter in ['pending', 'current', 'completed', 'failed']:
        projects = Project.objects.filter(status=status_filter)
    else:
        projects = Project.objects.all()
    return render(request, 'project/project_tab.html', {'projects': projects})


@login_required
def project_detail(request, pk):
    update_expired_projects()
    update_pending_projects()
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

    return render(request, 'project/project_detail.html', {
        'project': project,
        'comments': comments,
        'form': form
    })


@login_required
@is_project_manager_or_admin
def project_create(request):
    update_expired_projects()
    update_pending_projects()

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m()

            messages.success(request, 'Project created successfully!')

            try:
                team_size = project.assigned_users.count() or 3
                team_expertise = {
                    user.username: user.expertise for user in project.assigned_users.all()
                }

                subtasks = generate_subtasks(project.description, team_size,project.title)
                assignments = assign_tasks(team_expertise, project.description, team_size,project.title)

                for subtask in subtasks:
                    task = Task.objects.create(
                        title=subtask["title"],
                        description=subtask["description"],
                        project=project,
                        due_date=project.due_date,
                        status=subtask["status"],
                        priority=subtask["priority"],
                        progress=subtask["progress"]
                    )
                    assigned_names = assignments.get(subtask["description"], "")
                    usernames = [name.strip() for name in assigned_names.split(",") if name.strip()]
                    for username in usernames:
                        user = project.assigned_users.filter(username=username).first()
                        if user:
                            task.assigned_users.add(user)

                messages.success(request, '✅ AI subtasks generated and assigned!')
            except Exception as e:
                messages.error(request, f'AI task generation failed: {str(e)}')

            return redirect('project:project_tab')
    else:
        form = ProjectForm()

    return render(request, 'project/project_form.html', {'form': form})


@login_required
@is_project_manager_or_admin
def project_edit(request, pk):
    update_expired_projects()
    update_pending_projects()
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        form.save()
        return redirect('project_detail', pk=pk)

    return render(request, 'project/project_form.html', {'form': form})


@login_required
@is_project_manager_or_admin
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('project:project_tab')
    return render(request, 'project/project_confirm_delete.html', {'project': project})


@login_required
def project_tab(request):
    update_expired_projects()
    update_pending_projects()
    status_filter = request.GET.get('status')
    search_query = request.GET.get("search", "").strip()
    projects = Project.objects.all()
    if status_filter:
        projects = projects.filter(status=status_filter)
    if search_query:
        projects = projects.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    return render(request, 'project/project_tab.html', {'projects': projects})


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


@login_required
@is_project_manager_or_admin
def generate_subtasks_api(request):
    if request.method == "POST":
        project_description = request.POST.get("description")
        team_size = int(request.POST.get("team_size", 3))
        try:
            subtasks = generate_subtasks(project_description, team_size)
            return JsonResponse({"subtasks": subtasks})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST method allowed"}, status=405)
