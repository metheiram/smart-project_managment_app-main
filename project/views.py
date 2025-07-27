from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import Project
from .forms import ProjectForm, CustomUserCreationForm
from .utils import update_expired_projects, update_pending_projects
from .decorators import is_project_manager_or_admin
from tasks.models import Task
from project.ai_utils import assign_tasks, generate_subtasks
from notification.utils import notify_user

@login_required
def dashboard(request):
    update_expired_projects()
    update_pending_projects()
    if request.user.role == 'admin':
        projects = Project.objects.all()
    elif request.user.role == 'manager':
        projects = Project.objects.filter(created_by=request.user)
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

    if request.user.role == 'admin' or \
       (request.user.role == 'manager' and project.created_by == request.user) or \
       request.user in project.assigned_users.all():
        return render(request, 'project/project_detail.html', {'project': project})
    else:
        messages.error(request, "You do not have permission to view this project.")
        return redirect('project:project_tab')

@login_required
@is_project_manager_or_admin
def project_create(request):
    update_expired_projects()
    update_pending_projects()

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            if Project.objects.filter(title__iexact=title).exists():
                messages.error(request, f"⚠️ A project with the title '{title}' already exists.")
                return render(request, 'project/project_form.html', {'form': form})

            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()

            for user in project.assigned_users.all():
                notify_user(user, f"You have been added to the project: <strong>{project.title}</strong>.", "project_created", "/project/project_tab/")

            messages.success(request, '✅ Project created successfully!')

            try:
                team_size = project.assigned_users.count() or 3
                team_expertise = {user.username: user.expertise for user in project.assigned_users.all()}
                subtasks = generate_subtasks(project.description, team_size, project.title, project.due_date)
                assignments = assign_tasks(team_expertise, project.description, team_size, project.title, project.due_date)

                for subtask in subtasks:
                    task = Task.objects.create(
                        title=subtask["title"],
                        description=subtask["description"],
                        project=project,
                        due_date=subtask.get("due_date") or project.due_date,
                        status=subtask["status"],
                        priority=subtask["priority"],
                        progress=subtask["progress"]
                    )
                    usernames = [name.strip() for name in assignments.get(subtask["description"], "").split(",") if name.strip()]
                    for username in usernames:
                        user = project.assigned_users.filter(username=username).first()
                        if user:
                            task.assigned_users.add(user)
                            notify_user(user, f"You have been assigned a new task: <strong>{task.title}</strong> in project <strong>{project.title}</strong>.", "task_assigned", "/tasks/tab/")

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
        messages.success(request, '✅ Project updated successfully.')
        return redirect('project_detail', pk=pk)

    return render(request, 'project/project_form.html', {'form': form})

@login_required
@is_project_manager_or_admin
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, '🗑️ Project deleted successfully.')
        return redirect('project:project_tab')
    return render(request, 'project/project_confirm_delete.html', {'project': project})

@login_required
def project_tab(request):
    update_expired_projects()
    update_pending_projects()
    status_filter = request.GET.get('status')
    search_query = request.GET.get("search", "").strip()

    if request.user.role == 'admin':
        projects = Project.objects.all()
    elif request.user.role == 'manager':
        projects = Project.objects.filter(created_by=request.user)
    else:
        projects = Project.objects.filter(assigned_users=request.user)

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
        project_title = request.POST.get("title", "Untitled Project")
        project_due_date = request.POST.get("due_date")

        if not project_due_date:
            return JsonResponse({"error": "Missing required field: due_date"}, status=400)

        try:
            subtasks = generate_subtasks(project_description, team_size, project_title, project_due_date)
            return JsonResponse({"subtasks": subtasks})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST method allowed"}, status=405)

def projects_by_date(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)

    try:
        date = parse_date(date_str)
        projects = Project.objects.filter(due_date=date)
        project_data = [
            {
                'title': project.title,
                'description': project.description,
                'status': project.status,
            }
            for project in projects
        ]
        return JsonResponse({'projects': project_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
