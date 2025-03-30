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

def build_prompt_by_doc_type(query: str, contexts: list, doc_type: str, max_chars: int = 6000) -> str:
    context_text = ""
    for c in contexts:
        chunk = c["chunk"]
        if len(context_text) + len(chunk) > max_chars:
            break
        context_text += chunk + "\n---\n"
    
    if doc_type == "academic":
        return f"""
You are an expert academic assistant.
Answer the following question based on the document content. If appkicable, refer to research goals, methods, results, and conclusions.

Question:
{query}

Academic Document:
{context_text}

Answer:

""".strip()
    
    elif doc_type == "report":
        return f"""
You are an expert report assistant.
Answer the following question based on the document content.  Try to consider the document's purpose, key findings, and strategic recommendations.

Question:
{query}

Report Document:
{context_text}

Answer:
""".strip()

    elif doc_type == "manual":
        return f"""
You are an expert technical manual assistant.
Provide a clear, step-by-step answer or explanation based on the manual content.

Question:
{query}

Manual Document:
{context_text}

Answer:
""".strip()

    elif doc_type == "legal":
        return f"""
You are an expert legal assistant.
Answer the following question based on the document content. identify and explain relevant clauses, responsibilities, obligations, or rights.

Question:
{query}

Legal Document:
{context_text}

Answer:
""".strip()
    
    else:
        return f"""
You are an expert document assistant.
Answer the following question based on the document content.

Question:
{query}

Context:
{context_text}

Answer:
""".strip()

def build_single_summary_prompt(query: str, contexts: list, max_chars: int = 6000) -> str:
    context_text = ""
    for c in contexts:
        chunk = c["chunk"]
        if len(context_text) + len(chunk) > max_chars:
            break
        context_text += chunk + "\n---\n"

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
    return prompt.strip()


def build_joint_summary_prompt(query: str, summaries_files: dict) -> str:
    prompt = """You are a highly skilled language model assistant.

You are given summaries of multiple academic or technical documents. Please synthesize a single, concise and coherent summary that captures the shared purpose, differences (if relevant), and overarching contributions of these documents.

Each document is labeled below. Your response should be written clearly and suitable for someone who has not read the documents.

Document Summaries:
"""

    for index, (filename, summary) in enumerate(summaries_files.items(), start=1):
        prompt += f"\nDocument {index} ({filename}):\n{summary}\n"

    prompt += "\n\nUnified Summary:"
    return prompt.strip()


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
        prompt += f"\n**{index}. {filename}**\n{summary}\n\n"

    prompt += f"\n**Question:**\n{query}\n\n**Answer:**\n"
    return prompt.strip()

def build_prompt(query: str, contexts: list, max_chars: int = 6000) -> str:
    context_text = ""
    for c in contexts:
        chunk = c["chunk"]
        if len(context_text) + len(chunk) > max_chars:
            break
        context_text += chunk + "\n---\n"

    prompt = f"""
You are an expert assistant helping to analyze documents.
Answer the following question based on the document content.

Question:
{query}

Context:
{context_text}

Answer:
"""
    
    print(f"\n\nPrompt: {prompt}\n\n")
    return prompt.strip()

def generate_answer_for_summary(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional summarizer of technical and academic documents."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM summary generation error: {e}")
        return "An error occurred while generating the summary."


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
