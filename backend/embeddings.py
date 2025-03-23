from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_PATH = "data/embeddings/index.faiss"
METADATA_PATH = "data/embeddings/metadata.pkl"

# Load or initialize model
model = SentenceTransformer(MODEL_NAME)

def create_index():
    return faiss.IndexFlatL2(768)  # Dim for all-mpnet-base-v2

def save_index(index, metadata):
    os.makedirs(os.path.dirname("data/embeddings/"), exist_ok=True)
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

def search(query, top_k=3):
    index, metadata = load_index()
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), top_k)
    return [metadata[i] for i in I[0] if i < len(metadata)]

def split_text(text, max_len=512):
    """Simple splitter by sentence length. Can be enhanced."""
    sentences = text.split(". ")
    chunks, chunk = [], ""
    for sentence in sentences:
        if len(chunk) + len(sentence) < max_len:
            chunk += sentence + ". "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + ". "
    if chunk:
        chunks.append(chunk.strip())
    return chunks