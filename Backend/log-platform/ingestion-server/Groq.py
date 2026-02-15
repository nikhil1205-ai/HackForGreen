import json
import os
from groq import Groq

client = Groq(api_key="")
MODEL_NAME = "llama-3.3-70b-versatile"   

def analyze_log(message):
    prompt = f"""
You are a cyber security analyst.

Analyze this log message:

{message}

Explain:
- What is the issue?
- Possible reason?
- Risk level?
- Recommended fix?
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a professional cybersecurity analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq API Error: {str(e)}"

with open("data.json", "r", encoding="utf-8") as file:
    for line in file:
        log = json.loads(line.strip())

        if log.get("level") == "ERROR":
            print("\n==============================")
            print("Log ID:", log.get("id"))
            print("Message:", log.get("message"))

            analysis = analyze_log(log.get("message"))
            print("\nAI Analysis:\n")
            print(analysis)
