import os
import ast
from dotenv import load_dotenv
from groq import Groq
from django.contrib.auth import get_user_model
from tasks.models import Task

load_dotenv()

User = get_user_model()

def generate_subtasks(project_description, team_size, project_title, project_due_date):
    client = Groq(api_key=os.getenv("groq_API"))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
You are a smart project task generator.
Based on this project description: "{project_description}", generate exactly {team_size} subtasks.
For each subtask, provide:
- title
- description
- estimated_days
- due_date (required: must be a valid date string in format YYYY-MM-DD, evenly spaced before project deadline: {project_due_date})
- priority: ["low", "medium", "high", "critical"]
- status: ["not_started", "in_progress", "completed"]
- progress: 0–100 (default to 0 unless specified)
- project_title: "{project_title}"
Return only a list of dictionaries.
"""
            }
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
        temperature=0.7,
    )
    content = chat_completion.choices[0].message.content
    try:
        subtasks = ast.literal_eval(content.strip())
        for subtask in subtasks:
            subtask['progress'] = subtask.get('progress', 0)
            subtask['status'] = subtask.get('status', 'not_started')
            subtask['due_date'] = subtask.get('due_date', str(project_due_date))
        return subtasks
    except Exception as e:
        print("⚠️ Could not parse response as list of dictionaries:\n", content)
        print("Error:", e)
        return []

def assign_tasks(project_description, project_title, project_due_date, team_size,team_expertise,):
    # Fetch users with profile and expertise
    users = User.objects.filter(profile__isnull=False)
    team_expertise = {
        user.username: getattr(user.profile, 'expertise', 'general')
        for user in users
    }

    team_size = len(team_expertise)
    if team_size == 0:
        print("❌ No users with profile found.")
        return None

    # Generate subtasks
    subtasks = generate_subtasks(project_description, team_size, project_title, project_due_date)
    if not subtasks:
        print("❌ No subtasks generated. Exiting...")
        return None

    task_descriptions = [task["description"] for task in subtasks]

    # Assign tasks using AI based on real team expertise
    client = Groq(api_key=os.getenv("groq_API"))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
Act as a task assignment engine.

Users and their expertise:
{team_expertise}

Tasks:
{task_descriptions}

Assign each task to:
- One primary user (assignee)
- Optionally 1 or more supporting team members (team_members)

Only choose from the users provided.
Return in this format (no explanation):
{{
    "Task Title 1": {{"assignee": "USERNAME", "team_members": "USERNAME1, USERNAME2"}},
    "Task Title 2": ...
}}
"""
            }
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
        temperature=0.6,
    )

    content = chat_completion.choices[0].message.content
    try:
        assignments = ast.literal_eval(content.strip())
        print("✅ Final Assignments:\n", assignments)
        return assignments
    except Exception as e:
        print("⚠️ Failed to parse assignments:\n", content)
        print("Error:", e)
        return {}

def get_best_user_for_task(task_title):
    users_with_profile = User.objects.filter(profile__isnull=False)
    print("👥 Users with profile:", users_with_profile.count())

    if not users_with_profile.exists():
        print("❌ No users with profiles found.")
        return None

    task_title = task_title.lower()

    for user in users_with_profile:
        expertise = getattr(user.profile, 'expertise', '').lower()
        print(f"🔍 Checking {user.username} expertise: {expertise}")
        if expertise and (expertise in task_title or any(word in task_title for word in expertise.split())):
            print(f"✅ Matched: {user.username} for task: {task_title}")
            return user

    fallback_user = users_with_profile.first()
    print(f"⚠️ No match found. Falling back to: {fallback_user.username}")
    return fallback_user

