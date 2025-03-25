from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import List
import shutil
import os

from pdf_processing import process_uploaded_pdfs
from embeddings import embed_and_store, search, load_index, store_embedding_for_pdf, search_with_keywords
from llm import generate_answer, is_summary_query

app = FastAPI()

UPLOAD_DIR = "data/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_contexts_for_summary(metadata: list, max_chunks: int = 30):
    # unique, seen = [], set()
    # for item in metadata:
    #     chunk = item["chunk"]
    #     if chunk not in seen:
    #         seen.add(chunk)
    #         unique.append(item)
    #     if len(unique) >= max_chunks:
    #         break
    # return unique
    head = metadata[:max_chunks // 2]
    tail = metadata[-max_chunks // 2:]
    return head + tail

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
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_files = []
    for file in files:
        contents = await file.read()
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        store_embedding_for_pdf(file_path)
        uploaded_files.append(file.filename)
    return {"uploaded_files": uploaded_files}

@app.post("/query/")
def query_documents(query: str = Form(...), files: List[str] = Form(...)):
    try:
        index, metadata = load_index()
        filtered_metadata = [item for item in metadata if item["filename"] in files]

        if is_summary_query(query):
            contexts = get_contexts_for_summary(filtered_metadata)
        else:
            keyword_chunks = get_keyword_chunks(query, filtered_metadata, max_matches=3)
            vector_results = search(query, top_k=5)  # FAISS 벡터 검색을 없앤 경우 정확도가 확연히 떨어짐을 확인함함
            contexts = keyword_chunks + vector_results

        answer = generate_answer(query, contexts)
        return {
            "query": query,
            "answer": answer,
            "sources": contexts[:5]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear/")
def clear_data():
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    shutil.rmtree("data/embeddings", ignore_errors=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return {"message": "Data cleared successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
