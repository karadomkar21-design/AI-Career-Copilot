import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv("gemini.env")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
for model in client.models.list():
    print(model.name)
def analyze_resume(resume_text, user_goal):

    prompt = f"""
You are a senior software engineer and hiring manager.

Evaluate this resume.

User Goal:
{user_goal}

Return ONLY valid JSON.

{{
    "skills": [],
    "missing_skills": [],
    "roadmap": [],
    "interview_questions": []
}}

Resume:

{resume_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:

        return {
            "error": str(e)
        }

    # except Exception as e:
    #     return {
    #         "skills": [],
    #         "missing_skills": [],
    #         "roadmap": [],
    #         "interview_questions": [],
    #         "error": str(e)
    #     }
