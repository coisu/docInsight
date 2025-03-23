import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_prompt(query: str, contexts: list) -> str:
    context_text = "\n---\n".join([c["chunk"] for c in contexts])
    prompt = f"""
You are an expert assistant helping to analyze documents.
Answer the following question based on the provided document content.

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
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"LLM generation error: {e}")
        return "An error occurred while generating the answer."
