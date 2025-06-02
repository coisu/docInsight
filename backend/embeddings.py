from sentence_transformers import SentenceTransformer, util
import faiss
import numpy as np
import os
import re
import pickle
from pdf_processing import process_uploaded_pdfs
from models import model
from llm import guess_document_type, split_text, split_text_by_sections

# MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
# MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR = "data/embeddings"
os.makedirs(INDEX_DIR, exist_ok=True)
# INDEX_PATH = "data/embeddings/index.faiss"
# METADATA_PATH = "data/embeddings/metadata.pkl"

# FAISS is Approximate Nearest Neighbor (ANN) search library. 벡터 중 쿼리와 유사한 벡터값 찾기.근사값기준으로 top_k 청크 추출.
# It is vector search library, it is fast. but not the most accurate.
# semantic re-ranking is needed for better accuracy. FAISS가 가져온 top_k 청크를 다시 정렬하는 것.query_embedding과 각각의 chunk_embedding 사이의 cosine similarity 재계산.가장 의미적으로 가까운 순서로 정렬 
# cosine similarity is used for semantic search.
# FAISS supports inner product and L2 distance.
# To use cosine similarity with FAISS, normalize all vectors and use inner product.

# total docs contents (vector embedding)
# numerous embedded vectors (FAISS)
# Top 30 chunks (semantic search) -> re-ranking (cosine similarity)
# -> top 8 chunks (final answer)
# -> generate final answer (LLM)



# now changing the indexing for individual pdf files. individual FAISS and pkl


def create_index():
    # return faiss.IndexFlatL2(768) # 768 is the dimension of the embeddings from the model
    return faiss.IndexFlatIP(model.get_sentence_embedding_dimension())  # Using inner product for cosine similarity search

def save_individual_index(pdf_filename, index, metadata):
    base_filename = pdf_filename.replace('.pdf', '')
    index_path = os.path.join(INDEX_DIR, f"{base_filename}.faiss")
    meta_path = os.path.join(INDEX_DIR, f"{base_filename}.pkl")
    
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(index, index_path)
    with open(meta_path, "wb") as f:
        pickle.dump(metadata, f)

def load_individual_index(pdf_filename):
    base_filename = pdf_filename.replace('.pdf', '')
    index_path = os.path.join(INDEX_DIR, f"{base_filename}.faiss")
    meta_path = os.path.join(INDEX_DIR, f"{base_filename}.pkl")
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        print(f"Index or metadata for {pdf_filename} not found. Creating new index.")
        return create_index(), []
    try:
        index = faiss.read_index(index_path)
        with open(meta_path, "rb") as f:
            metadata = pickle.load(f)

    except Exception as e:
        print(f"Error loading index or metadata for {pdf_filename}: {e}. Returing new index.")
        return create_index(), []
    
    return index, metadata


def embed_and_store_individual(text_data):
    if not isinstance(text_data, list) or not text_data:
        print(f"Error: Invalid data format, got {type(text_data)}")
        return

    for item in text_data:
        if not isinstance(item, dict) or "text" not in item or "filename" not in item:
            print(f"Warning: Skipping invalid item in embed_and_store_individual: {item}")
            continue

        pdf_filename = item["filename"]
        text = item["text"]

        index, metadata = create_index(), []

        if not text.strip():
            print(f"Warning: Empty text for {pdf_filename}. Skipping.")
            save_individual_index(pdf_filename, index, metadata)
            continue
        
        doc_type = guess_document_type(text)
        # has_sections = bool(re.search(r'\b\d+(\.\d+)*\s+[^\n]+', text))
        # if doc_type == "academic" and has_sections:
        if doc_type == "academic" and bool(re.search(r'\b\d+(\.\d+)*\s+[A-Z]', text)): 
            chunks = split_text_by_sections(text)
        else:
            chunks = split_text(text)
        # chunks = split_text_by_sections(text) if doc_type == "academic" else split_text(text)
        if not chunks:
            print(f"No valid chunks found for {item['filename']} after splitting. Skipping.")
            save_individual_index(pdf_filename, index, metadata)
            continue    

        embeddings = model.encode(chunks)

        if embeddings.ndim == 1: # only one chunk, expand dimensions to 2D
            embeddings = np.expand_dims(embeddings, axis=0)
        if embeddings.size > 0:
            faiss.normalize_L2(embeddings)
            index.add(np.array(embeddings))
            current_file_metadata = [{"filename": pdf_filename, "chunk": chunk, "doc_type": doc_type} for chunk in chunks]
            metadata.extend(current_file_metadata)

        else:
            print(f"No embeddings generated for {pdf_filename}. Skipping.")
        
        save_individual_index(item["filename"], index, metadata)
        print(f"Stored embeddings for {pdf_filename} with {len(metadata)} chunks.")

def search_unified(query:str, filenames:list, top_k:int=50) -> list:
    if not query.strip() or not filenames:
        print("Error: Empty query or filenames list.")
        return []
    
    query_vec = model.encode([query])

    faiss.normalize_L2(query_vec)  # Normalize the query vector for cosine similarity

    combined_chunks_with_scores = []

    for filename in filenames:
        index, metadata = load_individual_index(filename)
        
        if index.ntotal == 0 or not metadata:
            print(f"No embeddings found for {filename}. Skipping.")
            continue

        distances, indices = index.search(query_vec, min(top_k, index.ntotal))
        
        for i in range(len(indices[0])):
            idx = indices[0][i]
            score = distances[0][i]
            if idx < len(metadata):
                combined_chunks_with_scores.append({"score": score, "data": metadata[idx]})
            else:
                print(f"Warning: Index {idx} out of bounds for metadata length {len(metadata)} in {filename}.")
    
    combined_chunks_with_scores.sort(key=lambda x: x["score"], reverse=True)

    final_top_k_chunks = [item["data"] for item in combined_chunks_with_scores[:top_k]]

    return final_top_k_chunks

def store_embedding_for_pdf(pdf_path: str):

    pdf_dir = os.path.dirname(pdf_path)

    filename = os.path.basename(pdf_path)
    text = ""
    try:
        from pdf_processing import extract_text_from_pdf
        text = extract_text_from_pdf(pdf_path)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return
    if text:
        text_data = [{"filename": filename, "text": text}]
        embed_and_store_individual(text_data)
    else:
        print(f"No text extracted from {pdf_path}. Skipping embedding.")


