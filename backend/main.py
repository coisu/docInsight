# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import List
import shutil
import os

from pdf_processing import process_uploaded_pdfs
from embeddings import embed_and_store, search
from llm import generate_answer

app = FastAPI()

UPLOAD_DIR = "data/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "Semantic Search + LLM API is running!"}

@app.post("/upload/")
def upload_pdf(files: List[UploadFile] = File(...)):
    """Uploads PDF files and stores them for processing."""
    uploaded_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_files.append(file.filename)

    # Extract text and embed
    extracted = process_uploaded_pdfs(UPLOAD_DIR)
    embed_and_store(extracted)

    return {"uploaded_files": uploaded_files, "status": "Processed and indexed."}

@app.post("/query/")
def query_documents(query: str = Form(...)):
    """Performs semantic search and returns LLM-generated answer."""
    try:
        results = search(query)
        answer = generate_answer(query, results)
        return {
            "query": query,
            "answer": answer,
            "sources": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
