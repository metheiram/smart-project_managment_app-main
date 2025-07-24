# project/ai_utils.py

import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY  # 🔐 You must add this key to .env or settings.py

from users.models import Profile
from django.contrib.auth import get_user_model
from tasks.models import Task




def generate_tasks_from_description(description):
    prompt = f"""
    Based on the following project description, generate a list of actionable tasks:
    "{description}"
    
    Format:
    1. Task title - short description
    2. ...
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can upgrade to GPT-4 later
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        tasks_text = response['choices'][0]['message']['content']
        return tasks_text.split("\n")  # Split each task
    except Exception as e:
        return [f"Error generating tasks: {e}"]

User = get_user_model()

def get_best_user_for_task(task_title):
    """
    Return the best user to assign this task to based on skill match and workload.
    """
    all_profiles = Profile.objects.all()
    candidates = []

    for profile in all_profiles:
        user = profile.user
        skills = profile.skills.lower().split(",")
        task_keywords = task_title.lower().split()

        match_score = sum(1 for word in task_keywords if word in skills)
        workload = Task.objects.filter(assignee=user, status__in=["not_started", "in_progress"]).count()

        candidates.append({
            "user": user,
            "match_score": match_score,
            "workload": workload
        })

    # Sort based on best skill match and least workload
    sorted_candidates = sorted(candidates, key=lambda c: (-c['match_score'], c['workload']))
    
    if sorted_candidates:
        return sorted_candidates[0]["user"]
    return None