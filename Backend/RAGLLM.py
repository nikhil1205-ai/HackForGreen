import csv
import os
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from functools import lru_cache


client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.1-8b-instant"   # Small + Fast


knowledge_logs = []



with open("data.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        level = row.get("level", "").strip().upper()
        message = row.get("message", "")

        if level == "ERROR" and message:
            knowledge_logs.append(message)


# If no logs found, avoid crash
if not knowledge_logs:
    knowledge_logs = ["No previous error logs available."]

# Build TF-IDF matrix once
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(knowledge_logs)


@lru_cache(maxsize=500)
def retrieve_context(query: str, top_k: int = 3) -> str:
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, tfidf_matrix)[0]

    top_indices = np.argsort(similarities)[-top_k:][::-1]
    results = [knowledge_logs[i] for i in top_indices]

    return "\n".join(results)


def analyze_log(message: str) -> str:
    context = retrieve_context(message)

    prompt = f"""
You are a cybersecurity analyst.

Similar past logs:
{context}

New log:
{message}

Provide:
- Issue
- Possible reason
- Risk level (LOW/MEDIUM/HIGH/CRITICAL)
- Recommended fix
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a professional cybersecurity analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Groq API Error: {str(e)}"


def ask_query(user_query: str) -> str:
    context = retrieve_context(user_query)

    prompt = f"""
You are a cybersecurity expert.

Relevant logs:
{context}

User question:
{user_query}

Provide a detailed answer.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Groq API Error: {str(e)}"
