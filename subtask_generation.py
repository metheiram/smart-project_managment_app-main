#pip install python-dotenv

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

import ast

def generate_subtasks(project_description, team_size):
    client = Groq(api_key=os.getenv("groq_API"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Generate {team_size} subtasks based on the following project description: {project_description}. Each subtask should be concise and actionable. Do not explain anything. Just return the subtasks in a dictionary format like: {{'task1': 'description1', 'task2': 'description2', ...}}",
            }
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
        temperature=0.7,
    )

    content = chat_completion.choices[0].message.content

    try:
        subtasks = ast.literal_eval(content.strip())
        print("Parsed Subtasks Dictionary:\n", subtasks)
        return subtasks
    except Exception as e:
        print("⚠️ Could not parse response as dictionary:\n", content)
        print("Error:", e)



