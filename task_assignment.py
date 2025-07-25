#pip install python-dotenv

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

import os
import ast
from dotenv import load_dotenv
from groq import Groq
from subtask_generation import generate_subtasks
# Load environment variables
load_dotenv()


project_description = "Develop a web application for task management with user authentication, task creation, and real-time updates."
team_size=3
team_expertise = {
    "ALI": ["python", "django", "javascript"],
    "ZAIN": ["javascript", "react", "nodejs"],
    "HINA": ["python", "flask", "sql"]
}


def assign_tasks(team_expertise, project_description, team_size):
    tasks = generate_subtasks(project_description, team_size)

    # Convert 'task1': 'description' → 'description': 'task1'
    reversed_task_map = {v: k for k, v in tasks.items()}
    task_descriptions = list(tasks.values())

    client = Groq(api_key=os.getenv("groq_API"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""Act as a task assignment system. Given the following team expertise: {team_expertise} and the generated tasks: {task_descriptions}, assign each task to the most suitable team member(s) based on their expertise. A task can be assigned to one or more members depending on complexity. 

                Only return a dictionary where keys are task descriptions and values are assigned member names (comma separated if multiple), like:
                {{'Design user authentication system': 'ALI, user2', 'Implement task creation and editing functionality': 'ZAIN'}}.

                Do not add any explanation or extra text — just return the dictionary.
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
        print("⚠️ Could not parse response as dictionary:\n", content)
        print("Error:", e)


assign_tasks(team_expertise, project_description, team_size)

