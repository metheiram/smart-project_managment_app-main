import os
import ast
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def generate_subtasks(project_description, team_size,project_title):
    client = Groq(api_key=os.getenv("groq_API"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
You are a smart project task generator.

Based on the following project description: "{project_description}", generate exactly {team_size} subtasks.

For each subtask, provide a dictionary with:
- title
- description
- estimated_days
- priority: ["low", "medium", "high", "critical"]
- status: ["not_started", "in_progress", "completed"]
- progress: 0–100 (default to 0 unless specified)
Also, include the project_title field and set its value to "{project_title}".
Return only the list of dictionaries. No explanation.
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
        return subtasks
    except Exception as e:
        print("⚠️ Could not parse response as list of dictionaries:\n", content)
        print("Error:", e)
        return []

def assign_tasks(team_expertise, project_description, team_size,project_title):
    subtasks = generate_subtasks(project_description, team_size,project_title)
    if not subtasks:
        print("❌ No subtasks generated. Exiting...")
        return None

    task_descriptions = [task["description"] for task in subtasks]

    client = Groq(api_key=os.getenv("groq_API"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
Act as a task assignment engine. Given team expertise: {team_expertise} and task descriptions: {task_descriptions}, assign each task to the most suitable team member(s). A task can be assigned to multiple members.

Return dictionary like:
{{"Create user auth": "ALI, USER2", "Design UI": "ZAIN"}}

No explanation.
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