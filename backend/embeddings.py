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
        chunks = split_text(text)
        embeddings = model.encode(chunks)
        index.add(np.array(embeddings))
        metadata.extend([{"filename": item["filename"], "chunk": chunk} for chunk in chunks])
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

def store_embedding_for_pdf(pdf_path: str):
    text_data = process_uploaded_pdfs(os.path.dirname(pdf_path))
    embed_and_store(text_data)



EXAMPLES = {
    "summary": [
        "summarize",
        "summarize this report",
        "summarize the whole document",
        "briefly describe the paper",
        "give me a summary",
        "analyze the paper",
        "what is this paper about",
        "what are these documents about",
        "give an overview of the documents",
        "provide a short summary",
        "shorten the text",
        "analyze this",
        "what do they discuss",
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
