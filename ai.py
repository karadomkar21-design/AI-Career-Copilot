import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a senior software engineer and hiring manager.

Evaluate the resume based on the user's goal.

User goal: "{user_goal}"

Return ONLY valid JSON.

{{
    "skills": [],
    "missing_skills": [],
    "roadmap": [],
    "interview_questions": []
}}

resume_text = resume_text[:3000]
Resume:
{resume_text}
"""
    print("API KEY FOUND:", API_KEY is not None)
    print("API KEY PREFIX:", API_KEY[:10] if API_KEY else "None")
    try:
        response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
        json={
        "model": "openai/gpt-oss-20b:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "response_format": {
        "type": "json_object"
        } 
    },
    timeout=(10, 20)
)

        response.raise_for_status()

        data = response.json()

        content = data["choices"][0]["message"]["content"].strip()

        # Remove markdown code fences if present
        content = content.replace("```json", "").replace("```", "").strip()

        return json.loads(content)
    except json.JSONDecodeError as e:
         print("\nJSON ERROR:", e)
         print("\nRAW RESPONSE:\n")
         print(content)
    raise

    # except Exception as e:
    #     return {
    #         "skills": [],
    #         "missing_skills": [],
    #         "roadmap": [],
    #         "interview_questions": [],
    #         "error": str(e)
    #     }
