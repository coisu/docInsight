import os
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from typing import List, Dict
from sentence_transformers import util
# from langchain.prompts import PromptTemplate
import re
from models import model

load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt_by_doc_type(query: str, contexts: list, doc_type: str, max_chars: int = 6000) -> str:
    context_text = ""
    included_chunks = []
    for c in contexts:
        chunk = c["chunk"]
        if len(context_text) + len(chunk) > max_chars:
            break
        context_text += chunk + "\n---\n"
        included_chunks.append(chunk)

    print("\n📥 ✅ Final included chunks in prompt (after max_chars limit):")
    for i, ch in enumerate(included_chunks):
        print(f"\n--- Included Chunk {i+1} ---\n{ch}\n")

# If the authors explicitly or implicitly mention any limitations, assumptions, constraints, or trade-offs, list them.
# If no limitations are stated, say: "The authors do not mention any limitations.
    if doc_type == "academic":
        return f"""
You are an expert academic assistant.
Answer the following question only based on the Academic content below. If appkicable, refer to research goals, methods, results, and conclusions.
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
Answer the following question only based on the document content.  Try to consider the document's purpose, key findings, and strategic recommendations.

Question:
{query}

Report Document:
{context_text}

Answer:
""".strip()

    elif doc_type == "manual":
        return f"""
You are an expert technical manual assistant.
Provide a clear, step-by-step answer or explanation only based on the manual content.

Question:
{query}

Manual Document:
{context_text}

Answer:
""".strip()

    elif doc_type == "legal":
        return f"""
You are an expert legal assistant.
Answer the following question only based on the document content. identify and explain relevant clauses, responsibilities, obligations, or rights.

Question:
{query}

Legal Document:
{context_text}

Answer:
""".strip()
    
    else:
        return f"""
You are an expert document assistant.
Answer the following question only based on the document content.

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
Answer the following question only based on the document content.

Question:
{query}

Context:
{context_text}

Answer:
"""
    
    print(f"\n\nPrompt: {prompt}\n\n")
    return prompt.strip()

async def generate_answer_for_summary(prompt: str) -> str:
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
        return await response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM summary generation error: {e}")
        return "An error occurred while generating the summary."


async def generate_answer_for_comparison(prompt: str) -> str:
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
        return await response.choices[0].message.content.strip()
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

async def generate_answer(prompt: str) -> str:
    try:
        response = await client.chat.completions.create(
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
        "summarize this",
        "summarize this document",
        "summarize this report",
        "summarize the whole content",
        "briefly describe the provided text",
        "give me a summary of the input",
        "what is this text about?",
        "what are these documents generally about?",
        "give an overview of the provided materials",
        "provide a short summary of all texts",
        "shorten the entire text provided",
        "high-level overview of the content",
        "tell me about these documents",
        "what's the main takeaway from this information?",
        "can you give me the gist of these papers?",
        "explain what these documents are generally discussing",
        "what is the overall purpose of this text?",
        "what are the main ideas discussed across these documents?",
        "provide a concise explanation of this material",
        "abstract this document for me"
    ],
    "comparison": [
        "compare these",
        "compare the provided documents",
        "contrast the given models",
        "what are the differences between the first and second text?",
        "what are the similarities between these two approaches?",
        "compare and contrast the methods described",
        "what is the difference between the two papers provided?",
        "how are these inputs different from each other?",
        "how are the concepts presented similar?",
        "compare this with that", 
        "contrast the first item with the second",
        "show differences from the other inputs",
        "find similarities to the other documents",
        "distinguish between these approaches",
        "highlight the key differences found",
        "compare concept A with concept B regarding their features",
        "what are the key distinctions between method X and method Y as presented?",
        "analyze the similarities and differences in the conclusions of study 1 and study 2", 
        "how does model Alpha differ from model Beta in terms of performance?",
        "evaluate the pros and cons of approach X versus approach Y based on these texts",
        "what is the relationship between idea A from the first document and idea B from the second?",
        "show the divergences between these two theories presented",
        "what are the relative merits of technique P compared to technique Q mentioned?",
        "how does item X measure up against item Y in terms of specified criteria?",
        "juxtapose the arguments presented in these articles"
    ],
    "normal": [ 
        "what specific dataset was used for the research mentioned?",
        "how many participants were involved in the described study?",
        "according to the text, what is the definition of [general term]?",
        "what are the key findings reported in section 3 of this document?",
        "what future research directions are suggested by the authors?",
        "what were the main conclusions of the experiment detailed in this report?",
        "explain the methodology used for data analysis in this study.",
        "what limitations of the current approach are discussed in this paper?",
        "what is the significance of [specific finding] mentioned in the text?",
        "describe the [specific process/algorithm] as outlined in this document.",
        "what was the [specific metric, e.g., F1 score] achieved by the model?",
        "how is [general concept] defined in the provided text?",
        "who are the authors of this work?",
        "what is the publication year of this document?",
        "what are the key findings?",
        "what future work do the authors suggest?",
        "what recommendations are made?",
        "what conclusions are drawn from this section?", # "this section"으로 범위 한정
        "what are the limitations mentioned by the authors?"
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
    lines = re.split(r'\n+', text)
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
    # section_pattern = re.compile(r'\b\d+(\.\d+)*\s+[^\n]+')  # e.g., "4.2 Next Sentence Prediction"
    
    section_pattern = re.compile(r'''
        ^                           # 줄 시작
        (                           
            (?:\d+(?:\.\d+)*)       # 1, 1.1, 1.1.1
            |(?:[IVXLCDM]+)         # Roman numerals (I, II, III,)
        )
        [\.\)\:\s]*                 # separator (dot, colon, space)
        [A-Z][^\n]{3,80}            # Uppercase, max 80 chars
        $
    ''', re.MULTILINE | re.VERBOSE)

    matches = list(section_pattern.finditer(text))

    chunks = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()

        sub_chunks = split_text(section_text, max_len=max_len, min_len=min_len)
        chunks.extend(sub_chunks)

    return chunks

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

def extract_keywords(query):
    return [word for word in query.lower().split() if word not in stop_words and len(word) > 2]

def semantic_filter_chunks(query, chunks, top_k=12):
    keywords = extract_keywords(query)
    print("🔍 Keywords for search:", keywords)
    keyword_embedding = model.encode(' '.join(keywords), convert_to_tensor=True)

    scored_chunks = []
    for chunk in chunks:
        chunk_embedding = model.encode(chunk["chunk"], convert_to_tensor=True)
        score = util.pytorch_cos_sim(keyword_embedding, chunk_embedding).item()
        scored_chunks.append((score, chunk))

    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    return [chunk for score, chunk in scored_chunks[:top_k]]