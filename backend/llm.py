import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
from sentence_transformers import util
from langchain.prompts import PromptTemplate
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def is_summary_query(query: str) -> bool:
#     query = query.lower().strip()
#     return any(q in query for q in [
#         "summarize", "summarize this report", "summarize the whole document", "briefly describe", "give me a summary", "analyze the paper",
#         "what is this paper about", "short summary", "shorten the text", "analyze this"
#     ])

# def is_comparison_query(query: str) -> bool:
#     query = query.lower().strip()
#     return any(q in query for q in [
#         "compare", "contrast", "difference", "differences", "similarities", "similar to", "different from", "compare and contrast", "compare with", "difference between"
#     ])

def build_prompt_by_doc_type(query: str, contexts: list, doc_type: str, max_chars: int = 6000) -> str:
    context_text = ""
    for c in contexts:
        chunk = c["chunk"]
        if len(context_text) + len(chunk) > max_chars:
            break
        context_text += chunk + "\n---\n"
    

# If the authors explicitly or implicitly mention any limitations, assumptions, constraints, or trade-offs, list them.
# If no limitations are stated, say: "The authors do not mention any limitations.
    if doc_type == "academic":
        return f"""
You are an expert academic assistant.
Answer the following question based on the Academic content below. If appkicable, refer to research goals, methods, results, and conclusions.
If the answer is not explicitly stated, try to infer it from context. If no information can be inferred, say so clearly.


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

# def generate_answer(query: str, contexts: list) -> str:
#     prompt = build_prompt(query, contexts)
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=1024,
#             temperature=0.7
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print(f"LLM generation error: {e}")
#         return "An error occurred while generating the answer."

def generate_answer(prompt: str) -> str:
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
    

    
EXAMPLES = {
    "summary": [
        "summarize",
        "summarize this report",
        "summarize the whole document",
        "briefly describe the paper",
        "give me a summary",
        "what is this paper about",
        "what are these documents about",
        "give an overview of the documents",
        "provide a short summary",
        "shorten the entire text",
        "high-level overview",
    ],
    "comparison": [
        "compare",
        "compare the documents",
        "contrast the models",
        "what are the differences",
        "what are the similarities",
        "compare and contrast the methods",
        "difference between the papers",
        "how are these different",
        "how are they similar",
        "compare with each other",
        "contrast this with that",
        "different from",
        "similar to",
        "distinguish between these",
        "highlight differences",
    ],
    "normal": [
    "what is the purpose of this document",            # could be taken as summary
    "what are the key findings",                      
    "what future work do the authors suggest",
    "what recommendations are made",
    "what conclusions are drawn",
    "what are the main ideas discussed",
    "what are the limitations mentioned",
]
}

def rerank_by_semantic_similarity(query: str, chunks: list, top_k: int = 8) -> list:
    query_embedding = model.encode(query, convert_to_tensor=True)

    scored = []
    for chunk in chunks:
        chunk_embedding = model.encode(chunk["chunk"], convert_to_tensor=True)
        score = util.pytorch_cos_sim(query_embedding, chunk_embedding).item()
        scored.append((score, chunk))

    # sort by score in descending order, most similar first
    scored.sort(reverse=True, key=lambda x: x[0])
    top_chunks = [chunk for _, chunk in scored[:12]]

    # deduplicate based on word overlap
    seen_words = set()
    diverse_chunks = []
    for chunk in top_chunks:
        words = set(chunk["chunk"].lower().split())
        if len(seen_words.intersection(words)) < 0.4 * len(words):
            diverse_chunks.append(chunk)
            seen_words.update(words)
        if len(diverse_chunks) >= top_k:
            break

    return diverse_chunks


def guess_document_type(text: str) -> str:
    text_lower = text.lower()

    academic_keywords = ["introduction", "experiment", "conclusion", "related work", "results", "evaluation", "dataset"]
    report_keywords = ["executive summary", "table of contents", "methodology", "findings", "objective", "recommendations"]
    manual_keywords = ["step 1", "usage:", "how to", "install", "instruction", "follow these steps"]
    legal_keywords = ["agreement", "terms and conditions", "clause", "party", "shall", "warranty", "liability", "indemnify"]

    if re.search(r'\b\d+(\.\d+)*\s+[A-Z]', text) and any(kw in text_lower for kw in academic_keywords):
        return "academic"
    if any(kw in text_lower for kw in report_keywords):
        return "report"
    if any(kw in text_lower for kw in manual_keywords):
        return "manual"
    if any(kw in text_lower for kw in legal_keywords):
        return "legal"
    return "general"


def classify_query_sementic(query: str, threshold: float = 0.6) -> str:
    query_embedding = model.encode(query, convert_to_tensor=True)
    type = "normal"
    score = 0

    for key, examples in EXAMPLES.items():
        example_embeddings = model.encode(examples, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(query_embedding, example_embeddings)
        max_score = scores.max().item() # this way is better for PyTorch tensors
        # max_score = max(scores.flatten())
        print(f"max_score: {max_score}")

        if max_score > threshold and max_score > score:
            score = max_score
            type = key

    return type

def split_text(text, max_len=800, min_len=200):
    lines = re.split(r'\n{2,}', text)
    # lines = text.split("\n")
    chunks = []
    current_chunk = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if len(current_chunk) + len(line) < max_len:
            current_chunk += line + "\n"
        else:
            if len(current_chunk.strip()) >= min_len:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"

    if len(current_chunk.strip()) >= min_len:
        chunks.append(current_chunk.strip())

    return chunks

def split_text_by_sections(text, max_len=800, min_len=200):
    section_pattern = re.compile(r'\b\d+(\.\d+)*\s+[^\n]+')  # e.g., "4.2 Next Sentence Prediction"
    matches = list(section_pattern.finditer(text))

    chunks = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()

        sub_chunks = split_text(section_text, max_len=max_len, min_len=min_len)
        chunks.extend(sub_chunks)

    return chunks
