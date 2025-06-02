from fastapi import FastAPI, UploadFile, File, HTTPException, Form
# from typing import List // python 3.8-
import shutil
import os

from pdf_processing import process_uploaded_pdfs
from embeddings import store_embedding_for_pdf, search_unified
from llm import generate_answer, build_comparison_prompt, generate_answer_for_comparison, build_joint_summary_prompt, generate_answer_for_summary, build_single_summary_prompt, build_prompt_by_doc_type, rerank_by_semantic_similarity, classify_query_sementic, semantic_filter_chunks
from collections import Counter
import re

import asyncio

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords


app = FastAPI()

UPLOAD_DIR = "data/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_contexts_for_summary(metadata: list, max_chunks: int = 30):
    head = metadata[:max_chunks // 2]
    tail = metadata[-max_chunks // 2:]
    return head + tail

def deduplicate_chunks(chunks):
    seen = set()
    unique = []
    for item in chunks:
        key = item['chunk'].strip()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

def get_head_tail_chunks(metadata, max_chunks=4):
    head = metadata[:max_chunks // 2]
    tail = metadata[-max_chunks // 2:]
    return deduplicate_chunks(head + tail)

@app.get("/")
async def root():
    return {"message": "Semantic Search + LLM API is running!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    uploaded_files_info = []
    for file_obj in files:
        contents = await file_obj.read()
        file_path = os.path.join(UPLOAD_DIR, file_obj.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        
        try:
            await asyncio.to_thread(store_embedding_for_pdf, file_path)
            uploaded_files_info.append({"filename": file_obj.filename, "status": "processed"})
        except Exception as e:
            print(f"Error processing file: {file_obj.filename}, {e}")
            uploaded_files_info.append({"filename": file_obj.filename, "status": "failed", "error": str(e)})
    return {"uploaded_files_info": uploaded_files_info}

async def generate_summary_async(query: str, contexts: list):
    single_prompt = build_single_summary_prompt(query, contexts)
    return await generate_answer_for_summary(single_prompt)


@app.post("/query/")
async def query_documents(query: str = Form(...), files: list[str] = Form(...)):
    try:
        print("\n\n>> Currently selected files for query:", files)
        # index, metadata = load_index()
        # filtered_metadata = [item for item in metadata if item["filename"] in files]

        query_type = classify_query_sementic(query)
        print(">> Query type:", query_type)

        retrieved_metadata_all_files = await asyncio.to_thread(search_unified, query, files, top_k=50)
        if not retrieved_metadata_all_files:
            return {
                "query": query,
                "answer": "No relevant documents found.",
                "sources": [],
                "query_type": query_type
            }
        
        final_answer = ""
        final_sources = []

        if query_type == "summary":
            contexts_by_file = {file_name: [] for file_name in files}
            for item in retrieved_metadata_all_files:
                if item["filename"] in contexts_by_file:
                    contexts_by_file[item["filename"]].append(item)
            
            summary_tasks = []
            valid_files_for_summaries = []

            for file_name, contexts in contexts_by_file.items():
                if contexts:
                    summary_tasks.append(generate_summary_async("summarize this document", contexts[:10]))
                    valid_files_for_summaries.append(file_name)

            if not summary_tasks:
                final_answer = "No valid contexts found for summarization."
            else:
                individual_summaries_results = await asyncio.gather(*summary_tasks)

                summaries_files = {}
                for i, file_name in enumerate(valid_files_for_summaries):
                    summaries_files[file_name] = individual_summaries_results[i]

                prompt_summary = build_joint_summary_prompt(query, summaries_files)
                final_answer = await generate_answer_for_summary(prompt_summary)

                final_sources = [
                    {
                        "filename": file,
                        "summary_chunk": summaries_files.get(file, "N/A"),
                        "original_top_chunks_count": len(contexts_by_file.get(file, [])[:10]),
                    } for file in valid_files_for_summaries
                ]
            
        elif query_type == "comparison":
            if len(files) > 1:
                contexts_by_file = {file_name: [] for file_name in files}
                for item in retrieved_metadata_all_files:
                    if item["filename"] in contexts_by_file:
                        contexts_by_file[item["filename"]].append(item)

                summary_tasks = []
                valid_files_for_comparison = []

                for file_name, contexts in contexts_by_file.items():
                    if contexts:
                        summary_tasks.append(generate_summary_async("summarize this document", contexts[:10]))
                        valid_files_for_comparison.append(file_name)

                if not summary_tasks:
                    final_answer = "No valid contexts found for comparison."
                else:
                    individual_summaries_results = await asyncio.gather(*summary_tasks)

                    summaries_files = {}
                    for i, file_name in enumerate(valid_files_for_comparison):
                        summaries_files[file_name] = individual_summaries_results[i]

                    prompt_comparison = build_comparison_prompt(query, summaries_files)
                    final_answer = await generate_answer_for_comparison(prompt_comparison)

                    final_sources = [
                        {
                            "filename": file,
                            "summary_chunk": summaries_files.get(file, "N/A"),
                            "original_top_chunks_count": len(contexts_by_file.get(file, [])[:10]),
                        } for file in valid_files_for_comparison
                    ] 

            elif len(files) == 1:
                single_file = files[0]
                single_file_metadata = [item for item in retrieved_metadata_all_files if item["filename"] == single_file]

                if not single_file_metadata:
                    final_answer = "No valid contexts found for comparison."
                else:
                    relevant_contexts = await asyncio.to_thread(rerank_by_semantic_similarity, query, single_file_metadata, top_k=8)

                    if not relevant_contexts:
                        final_answer = f"No relevant contexts found for comparison in {single_file}."
                    else:
                        print(f"\n📌 Selected final context chunks for single-file comparison from {single_file}:")
                        for i, ctx in enumerate(relevant_contexts):
                            print(f"\n--- Context {i+1} ---\n{ctx['chunk']}\n")

                            dominant_doc_type = relevant_contexts[0].get("doc_type", "general")
                            prompt_comparison_single = build_prompt_by_doc_type(
                                f"Answer the questions based on following context, {query}:", 
                                relevant_contexts, 
                                dominant_doc_type
                            )
                            final_answer = await generate_answer(prompt_comparison_single)
                            final_sources = relevant_contexts

            else:
                final_answer = "No valid contexts found for comparison."
         
        else: # normal query processing
            relevant_contexts = await asyncio.to_thread(rerank_by_semantic_similarity, query, retrieved_metadata_all_files, top_k=8)

            if not relevant_contexts:
                final_answer = "No relevant contexts found."
            else:
                print(f"\n📌 Selected final context chunks for query:")
                for i, ctx in enumerate(relevant_contexts):
                    print(f"\n--- Context {i+1} ---\n{ctx['chunk']}\n")

                doc_type_counts = Counter(ctx.get("doc_type", "general") for ctx in relevant_contexts)
                dominant_doc_type = doc_type_counts.most_common(1)[0][0] if doc_type_counts else "general"

                prompt = build_prompt_by_doc_type(query, relevant_contexts, dominant_doc_type)
                final_answer = await generate_answer(prompt)
                final_sources = relevant_contexts
        
        return {
            "query": query,
            "answer": final_answer,
            "sources": final_sources,
            "query_type": query_type
        }

    except Exception as e:
        print(f"Error in query processing: {e}")
        import traceback
        traceback.print_exc() # stack trace for debugging
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear/")
async def clear_data():
    try:
        await asyncio.to_thread(shutil.rmtree, UPLOAD_DIR, ignore_errors=True)
        await asyncio.to_thread(shutil.rmtree, "data/embeddings", ignore_errors=True)
        await asyncio.to_thread(os.makedirs, UPLOAD_DIR, exist_ok=True)
        await asyncio.to_thread(os.makedirs, "data/embeddings", exist_ok=True)
    except Exception as e:
        print(f"Error clearing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing data:{str(e)}")
    return {"message": "Data cleared successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
