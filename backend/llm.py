import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_summary_query(query: str) -> bool:
    query = query.lower().strip()
    return any(q in query for q in [
        "summarize", "summarize this report", "summarize the whole document", "briefly describe", "give me a summary", "analyze the paper",
        "what is this paper about", "short summary", "shorten the text", "analyze this"
    ])

def is_comparison_query(query: str) -> bool:
    query = query.lower().strip()
    return any(q in query for q in [
        "compare", "contrast", "difference", "differences", "similarities", "similar to", "different from", "compare and contrast", "compare with", "difference between"
    ])

def build_comparison_prompt(query: str, summaries_files: dict) -> str:
    prompt = """You are an expert in analyzing multiple academic papers.

Compare the uploaded documents based on their key objectives, methods, and conclusions. 
Identify commonalities and differences. If there are **no significant similarities**, explicitly say so.

Structure the answer like this:

1. Overall Topic Summary (if applicable)
2. 📄 Document-by-document Summary
3. Key Differences
4. Commonalities (or state "None found.")
5. Insights or Implications

Summaries of the uploaded documents:
"""
    for index, (filename, summary) in enumerate(summaries_files.items(), start=1):
        prompt += f"\n**{index}. {filename}**\n{summary}\n"

    prompt += f"\n**Question:**\n{query}\n\n**Answer:**\n"
    return prompt.strip()

def build_prompt(query: str, contexts: list, max_chars: int = 6000) -> str:
    context_text = ""
    for c in contexts:
        chunk = c["chunk"]
        if len(context_text) + len(chunk) > max_chars:
            break
        context_text += chunk + "\n---\n"

    if is_summary_query(query):
        prompt = f"""
You are an expert document summarizer.

Summarize the content clearly and concisely, suitable for someone who has not read the document. 
If applicable, include the following:

- The main purpose and scope of the document
- Key findings or insights
- Important methods, arguments, or processes
- Implications, conclusions, or future directions

Try to organize the summary into the following structure if appropriate:

Title:
...

Summary:
...

Highlights:
- ...
- ...
- ...

Conclusion:
...

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


def generate_answer_for_comparison(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in analyzing multiple academic papers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM generation error: {e}")
        return "An error occurred while generating the answer."

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
