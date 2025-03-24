from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import List
import shutil
import os

from pdf_processing import process_uploaded_pdfs
from embeddings import embed_and_store, search, load_index, store_embedding_for_pdf
from llm import generate_answer, is_summary_query

app = FastAPI()

UPLOAD_DIR = "data/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_contexts_for_summary(metadata: list, max_chunks: int = 30):
    unique, seen = [], set()
    for item in metadata:
        chunk = item["chunk"]
        if chunk not in seen:
            seen.add(chunk)
            unique.append(item)
        if len(unique) >= max_chunks:
            break
    return unique

def get_keyword_chunks(query: str, metadata: list, max_matches=3):
    keywords = query.lower().split()
    matches = []
    for item in metadata:
        content = item["chunk"].lower()
        if any(k in content for k in keywords):
            matches.append(item)
        if len(matches) >= max_matches:
            break
    return matches

@app.get("/")
def root():
    return {"message": "Semantic Search + LLM API is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # 기존 파일 및 임베딩 삭제
    if os.path.exists("data/pdfs"):
        for f in os.listdir("data/pdfs"):
            os.remove(os.path.join("data/pdfs", f))
    if os.path.exists("data/embeddings/index.faiss"):
        os.remove("data/embeddings/index.faiss")
    if os.path.exists("data/embeddings/metadata.pkl"):
        os.remove("data/embeddings/metadata.pkl")

    # 새 파일 저장
    contents = await file.read()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    # 새 임베딩 생성
    store_embedding_for_pdf(filepath)
    return {"filename": file.filename}

@app.post("/query/")
def query_documents(query: str = Form(...)):
    try:
        index, metadata = load_index()

        if is_summary_query(query):
            contexts = get_contexts_for_summary(metadata)
        else:
            search_results = search(query, top_k=5)
            keyword_chunks = get_keyword_chunks(query, metadata)
            contexts = keyword_chunks + search_results

        answer = generate_answer(query, contexts)
        return {
            "query": query,
            "answer": answer,
            "sources": contexts[:5]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
