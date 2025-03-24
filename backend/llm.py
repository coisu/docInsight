import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_summary_query(query: str) -> bool:
    query = query.lower().strip()
    return any(q in query for q in [
        "summarize", "summarize this report", "summarize the whole document", "briefly describe"
    ])

def build_prompt(query: str, contexts: list, max_chars: int = 6000) -> str:
    context_text = ""
    for c in contexts:
        chunk = c["chunk"]
        if len(context_text) + len(chunk) > max_chars:
            break
        context_text += chunk + "\n---\n"

    if is_summary_query(query):
        prompt = f"""
You are a professional document summarizer.
Summarize the document clearly and concisely. Use structured sections if applicable.

Document:
{context_text}

Summary:
"""
    else:
        prompt = f"""
You are an expert assistant helping to analyze documents.
Answer the following question based on the document content.

Question:
{query}

Context:
{context_text}

Answer:
"""
    return prompt.strip()

def generate_answer(query: str, contexts: list) -> str:
    prompt = build_prompt(query, contexts)
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM generation error: {e}")
        return "An error occurred while generating the answer."
