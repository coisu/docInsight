from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import List
import shutil
import os

from pdf_processing import process_uploaded_pdfs
from embeddings import embed_and_store, search, load_index, store_embedding_for_pdf, search_with_keywords, classify_query_sementic
from llm import generate_answer, is_summary_query, is_comparison_query, build_comparison_prompt, generate_answer_for_comparison, build_joint_summary_prompt, generate_answer_for_summary, build_single_summary_prompt, build_prompt_by_doc_type

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

def deduplicate_chunks(chunks):
    seen = set()
    unique = []
    for item in chunks:
        key = item['chunk'].strip()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

def diverse_top_chunks(chunks, k=8):
    selected = []
    seen_words = set()
    for chunk in chunks:
        words = set(chunk["chunk"].lower().split())
        if len(seen_words.intersection(words)) < 0.4 * len(words):  # 40% 이상 겹치면 유사한 내용으로 판단
            selected.append(chunk)
            seen_words.update(words)
        if len(selected) >= k:
            break
    return selected

def get_head_tail_chunks(metadata, max_chunks=4):
    head = metadata[:max_chunks // 2]
    tail = metadata[-max_chunks // 2:]
    return deduplicate_chunks(head + tail)

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
        print("\n\n📂 Currently selected files for query:", files)
        index, metadata = load_index()
        filtered_metadata = [item for item in metadata if item["filename"] in files]

        query_type = classify_query_sementic(query)
        
        print("🔍 Query type:", query_type)

        if query_type == "summary":
            contexts_files = {file: [] for file in files}
            for item in filtered_metadata:
                contexts_files[item["filename"]].append(item)

            summaries_files = {}
            for file, contexts in contexts_files.items():
                single = build_single_summary_prompt("summarize this document", contexts[:10])
                summary = generate_answer_for_summary(single)
                summaries_files[file] = summary
            
            prompt_summary = build_joint_summary_prompt(query, summaries_files)
            summarized_answer = generate_answer_for_summary(prompt_summary)
            
            return {
                "query": query,
                "answer": summarized_answer,
                "sources": [
                    {
                        "filename": file, "chunk": summaries_files[file],
                        "original_chunks": [c["chunk"] for c in contexts_files[file]]
                    } for file in summaries_files
                ],
                "query_type": query_type
            }
        
            # contexts = get_contexts_for_summary(filtered_metadata)
        elif query_type == "comparison":
            contexts_files = {file: [] for file in files}
            for item in filtered_metadata:
                contexts_files[item["filename"]].append(item)
            
            summaries_files = {}
            for file, contexts in contexts_files.items():
                summary = generate_answer("summarize this document", contexts[:10])
                summaries_files[file] = summary

            prompt_comparison = build_comparison_prompt(query, summaries_files)
            compared_answer = generate_answer_for_comparison(prompt_comparison)
            return {
                "query": query,
                "answer": compared_answer,
                "sources": [
                    {
                        "filename": file, "chunk": summaries_files[file],
                        "original_chunks": [c["chunk"] for c in contexts_files[file]]
                    } for file in summaries_files
                ],
                "query_type": query_type
            }
        
        else:
            from collections import Counter

            doc_type_counter = Counter([item.get("doc_type", "unknown") for item in filtered_metadata])
            dominant_doc_type = doc_type_counter.most_common(1)[0][0]

            head_tail = get_head_tail_chunks(filtered_metadata, max_chunks=4)
            keyword_chunks = get_keyword_chunks(query, filtered_metadata, max_matches=3)
            vector_results = search(query, top_k=12)  # FAISS 벡터 검색을 없앤 경우 정확도가 확연히 떨어짐을 확인함
            vector_results = [item for item in vector_results if item["filename"] in files]
            
            raw_chunks = head_tail + keyword_chunks + vector_results
            filtered_chunks = deduplicate_chunks(raw_chunks)
            contexts = diverse_top_chunks(filtered_chunks, k=8)

            # if is_academic:
            #     prompt_summary = build_single_summary_prompt(query, filtered_metadata[:10])
            #     summarized_answer = generate_answer_for_summary(prompt_summary)
            prompt = build_prompt_by_doc_type(query, contexts, dominant_doc_type)
            answer = generate_answer(prompt)

            return {
                "query": query,
                "answer": answer,
                "sources": filtered_metadata[:8],
                "query_type": query_type
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
