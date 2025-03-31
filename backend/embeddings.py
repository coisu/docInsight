from sentence_transformers import SentenceTransformer, util
import faiss
import numpy as np
import os
import pickle
from pdf_processing import process_uploaded_pdfs


MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_PATH = "data/embeddings/index.faiss"
METADATA_PATH = "data/embeddings/metadata.pkl"

# Load model
model = SentenceTransformer(MODEL_NAME)

# FAISS is Approximate Nearest Neighbor (ANN) search library.
# It is vector search library, it is fast. but not the most accurate.
# semantic re-ranking is needed for better accuracy.
# cosine similarity is used for semantic search.
# FAISS supports inner product and L2 distance.
# To use cosine similarity with FAISS, normalize all vectors and use inner product.


def create_index():
    return faiss.IndexFlatL2(768)

def save_index(index, metadata):
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

def load_index():
    if not os.path.exists(INDEX_PATH):
        return create_index(), []
    index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def embed_and_store(text_data):
    index, metadata = load_index()
    for item in text_data:
        text = item["text"]
        if not text.strip():
            continue
        
        doc_type = guess_document_type(text)
        print(f"\n\n>> Document type: {doc_type}\n\n")
        if doc_type == "academic":
            chunks = split_text_by_sections(text)
        else:
            chunks = split_text(text)

        embeddings = model.encode(chunks)
        index.add(np.array(embeddings))
        metadata.extend([{"filename": item["filename"], "chunk": chunk, "doc_type": doc_type} for chunk in chunks])
    save_index(index, metadata)

def search(query, top_k=10):
    index, metadata = load_index()
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), top_k)
    return [metadata[i] for i in I[0] if i < len(metadata)]

def search_with_keywords(query, metadata, top_k=10):
    query_vec = model.encode([query])
    index = create_index()
    chunks = []
    for item in metadata:
        embedding = model.encode([item["chunk"]])
        index.add(np.array(embedding))
        chunks.append(item)
    
    D, I = index.search(np.array(query_vec), top_k)
    return [chunks[i] for i in I[0] if i < len(chunks)]

import re

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

def store_embedding_for_pdf(pdf_path: str):
    text_data = process_uploaded_pdfs(os.path.dirname(pdf_path))
    embed_and_store(text_data)

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
