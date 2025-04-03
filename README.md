# DocInsight
- Semantic Search + LLM Project

## Project Overview
This project is designed to enable **semantic search across multiple PDF documents**, followed by **LLM-powered summarization and answer generation**. It leverages vector similarity to identify semantically relevant text chunks and constructs logical, concise responses using a large language model.

## Project Objectives
- Enable users to quickly find relevant information through **semantic search**.
- Provide **LLM-powered summarization** of retrieved documents for coherent and logical answers.
- Develop a **browser-accessible web interface** for seamless user interaction.
- Utilize **Docker for containerized deployment** to ensure easy setup and execution.

## 🚀 Features

- **Semantic Search**: Retrieves the most relevant chunks from uploaded PDFs using embedding-based similarity.
- **LLM Integration**: Summarizes and constructs coherent answers based on the selected chunks.
- **Multi-file Support**: Capable of handling multiple PDF files uploaded via browser interface.
- **Browser-based Interface**: Built for accessibility and convenience directly from the web.

## 🛠️ Tech Stack

- Python
- Docker & Docker Compose
- PDF processing: `PyMuPDF` / `pdfplumber`
- Embeddings & Semantic Search: `SentenceTransformers`, `FAISS`
- LLM Inference: OpenAI API / Local models (optional)



## 🚀 Development & Execution
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/coisu/docInsight.git
cd docInsight
```

### 2️⃣ Run the Docker Containers
> The `.env` file is encrypted using GDG, and you'll need the decryption password to load environment variables.
> You would need your own OPENAI_API_KEY setting

```bash
make build
make run
```

### 3️⃣ Access the Web Interface
```
http://localhost:8501  (Streamlit UI)
http://localhost:8000/docs  (FastAPI Swagger UI)
```

## 📌 Planned Improvements

- [x]  **Semantic Query Classification**  
  Classify incoming queries as `summary`, `comparison`, or `normal` using sentence embeddings and cosine similarity.  
  → Replaced keyword-based detection with semantic similarity; tested with both direct and indirect question phrasing.

- [x]  **Original Context Preview for Summary & Comparison**  
  Return original document chunks (`original_chunks`) along with generated summaries and comparisons.  
  → Enables full traceability in the frontend by displaying both the answer and its supporting source.

- [x]  **File Selection for Targeted QA**  
  Allow users to manually select which uploaded PDF files to include in a query.  
  → Fully implemented at both frontend and backend levels.

- [x]  **Smarter Context Selection**
  improving how document chunks are selected for answering user questions,
  - [x] Paragraph-based chunking instead of line-based splitting to preserve semantic structure.
  - [x] Deduplication and diversity filtering to avoid repetitive or overly similar chunks.
  - [x] Head–Tail inclusion to ensure important introduction and conclusion sections are always considered.
  - [x] Document-type detection to apply different chunking strategies for academic papers, reports, manuals, and general texts.
  - [x] Section-aware Chunking for Academic Documents
  - [x] 🚧 re-ranking chuks after getting them by FAISS. vetor search is not accurate enough for some questions. apply cosine similarity caculation on it.

- [ ] 🚧 **Prompt Engineering & Context Selection Optimization**  
  Improve retrieval precision and summarization quality by:  
  - controlling prompt length  
  - combining keyword-based and vector-based chunk selection  
  - exploring highlight-based chunk prioritization

- [ ] 🚧 **Robust Handling of Multi-Document Reasoning**  
  Continue testing complex multi-file questions, especially those requiring reasoning across 2 or 3 specific documents.  
  → Includes indirect, comparison, and hybrid question types for reliability testing.

- [ ]  **Scalability for Large Document Sets**  
  Optimize indexing, chunking, and memory usage to support 50+ PDF documents without performance degradation.  
  → Refactor chunk loading, vector storage, and file filtering pipeline.

- [ ]  **Improved Frontend UI/UX**  
  Refine document selection interface (multi-select dropdown, file chunk preview) and show per-query type indicators (`summary`, `comparison`, `normal`).

- [ ]  **Multi-language Support**  
  Extend semantic search and question answering to non-English documents, starting with Korean and French support.

- [x]  **Debugging & Explainability Tools**  
  Add developer-facing tools to log and visualize:  
  - selected chunks and similarity scores  
  - how each chunk contributed to the answer  
  - query classification reasoning (e.g., cosine similarity value)


-------------------

### 📌 Result Generator Development

> Currently supporting multi-document queries with dynamic answer generation based on query type.  
> The query type is determined using `classify_query_sementic()` in `embeddings.py`.

---
### Uploaded Files
- `RoBERTa.pdf`
- `language_understanding_paper.pdf`
- `1810.04805v2.pdf`

## Question - 1 - Multi-document Summary
> *"Help me understand the general direction of these documents."*

This query was intentionally designed to **avoid direct keywords** like “summarize” to test whether the classification via semantic embeddings works as expected.

---
### ✅ Result
> The system correctly identified this as a `summary` query and returned:  
> - Summaries for each uploaded document  
> - Toggleable views to inspect the original document chunks used to generate the summaries

#### Screenshots
  
  **Query + Answer UI**
  
  ![multiple_sum_ques](https://github.com/user-attachments/assets/9ee0b54f-9b82-40f8-839f-508c36cd98a8)
  ![multiple_sum_ans](https://github.com/user-attachments/assets/ad1b74e7-dcac-4175-9e73-88f807f7ffe6)
  
  **Summaries per Document**
  
  ![multiple_sum_1](https://github.com/user-attachments/assets/8dc97613-b00e-4f26-a314-73bb9a835b04)
  ![multiple_sum_2](https://github.com/user-attachments/assets/75311945-af4e-47d1-8c3a-bae597eb9c8c)
  ![multiple_sum_3](https://github.com/user-attachments/assets/32b0a237-bfe1-4d37-953f-7c31d9987e9f)

  **Original Source Chunk Viewer**
  
  ![multiple_sum_1_origin](https://github.com/user-attachments/assets/0d7ccb0f-ee63-4a13-ace9-22fd0bb2f7dc)


---

## Question - 2 - Multi-document Differentiation
> *"What are the key takeaways that distinguish each paper?"*

Although the query does not include direct comparison keywords like “compare” or “difference”, it was accurately classified as a `comparison` thanks to the semantic understanding logic.

---

### ✅ Result
> The system handled the `comparison` query by returning a structured, multi-part answer including:  
> - An overall topic summary  
> - Per-document summaries  
> - Key differences  
> - Commonalities  
> - Insights and implications  
> - Toggleable views for original source chunks

- #### Screenshots
  
  **Query + Answer UI**

  ![multiple_diff_ques](https://github.com/user-attachments/assets/bba2e04d-be7b-4224-9596-bfe5205683ac)
  ![multiple_diff_ans1](https://github.com/user-attachments/assets/bc9111d3-b65a-4229-9a71-6f336a2dcd28)
  ![multiple_diff_ans2](https://github.com/user-attachments/assets/4fb04653-fd50-4d80-b496-46978f66e178)

  **Summaries per Document**
  
  ![multiple_diff_srcs1](https://github.com/user-attachments/assets/2acd0152-afb8-466e-b684-1a267f258477)
  ![multiple_diff_srcs2](https://github.com/user-attachments/assets/6a7ea744-bbb5-4991-8e13-a6d5cdf5726b)

  **Original Source Chunk Viewer**

  ![multiple_diff_origin1](https://github.com/user-attachments/assets/38ee93d7-f128-4ada-af02-5df71aca990c)
  ![multiple_diff_origin2](https://github.com/user-attachments/assets/85fff2c5-bd30-4d96-80e1-8804732ccb25)


---

These examples validate that the app:
- Understands query intent even when phrased naturally
- Differentiates between summary and comparison needs
- Dynamically generates structured responses using multiple documents
- Provides full traceability to original source content



---



## Summary of Improvements - 03042025
Enhanced Chunking Logic for Academic PDF Documents
This update significantly improves the chunk generation process to better support academic document Q&A tasks. The following changes were made:

1. Improved Section Header Detection
  Previous regex only matched numeric section headers (e.g., 4.2 Section Name)
  New regex supports various academic patterns:

    Arabic numbers: `1`, `2.3`, `3.1.4`
    Roman numerals: `I.`, `II)`, etc.
    Keywords like “Section 1: Introduction”
    Standalone capitalized section titles

2. Refined Line-Based Chunk Splitting
  Replaced `re.split(r'\n{2,}', text)` with `re.split(r'\n+', text)`
  Enables chunking even when documents don't contain double line breaks

3. Increased Candidate Chunks for Reranking (`search_unified()`)
  Increased `top_k` in FAISS search from 20 → 50 to significantly improve relevant chunk recall for long academic documents.

---

### Before vs After: 
#### Test case1 
##### Q1. What are the key differences in the training objectives between BERT and RoBERTa?


#### A - Before
  > The document does not provide explicit information on the differences in training objectives between BERT and RoBERTa.
However, it mentions that **BERT uses two main objectives** for pretraining: **Masked Language Modeling (MLM)** and **Next Sentence Prediction (NSP)**. For MLM, a random sample of tokens in the input sequence is selected and replaced with a special token [MASK], and the objective is to predict these masked tokens. For NSP, the objective is to predict whether two segments follow each other in the original text. However, **the document does not provide specific information on the training objectives of RoBERTa.**
  
#### A - After
  > The key differences in the training objectives between BERT and RoBERTa are primarily related to **data processing and optimization techniques.**
BERT uses two objectives during pretraining: masked language modeling and next sentence prediction. It masks a random sample of input tokens and uses a cross-entropy loss function to predict the masked tokens. BERT also trains on two segments of token sequences, presented as a single input sequence with special tokens delimiting them.
  >
  > On the other hand, RoBERTa's training objectives focus on **longer training times, larger batches**, and **more data**. It also **removes the next sentence prediction objective used by BERT**, trains on **longer sequences**, and **dynamically changes the masking pattern** applied to the training data. RoBERTa is also trained with a **batch size eight times larger** for half as many optimization steps, thus seeing four times as many sequences in pretraining compared to BERT. Also, unlike BERT, RoBERTa's training procedure does **not involve multi-task finetuning** or additional data for certain tasks.

---

#### Test case2
##### Q2. Compare the experimental results of BERT and RoBERTa on GLUE and SQuAD benchmarks.

#### A - Before
  > The academic document **does not provide specific experimental results** for BERT and RoBERTa on GLUE and SQuAD benchmarks. However, it is mentioned that the **RoBERTa model, when trained for 500K steps, outperforms XLNetLARGE** across most tasks. It is also stated that the **best RoBERTa model achieves state-of-the-art results** on GLUE, RACE and SQuAD. For BERT, it is mentioned that it was **significantly undertrained** and can **match or exceed the performance** of every model published after it. **Further detail or comparison of the results is not provided.**

#### A - After
  > The academic document **does not provide explicit numerical comparisons** between the BERT and RoBERTa models on the GLUE and SQuAD benchmarks. However, it mentions that the **improved training procedure of RoBERTa improves upon the published BERT results** on both GLUE and SQuAD. When RoBERTa was trained for longer over additional data, it **achieved a score of 88.5 on the public GLUE leaderboard**, matching the **88.4 reported by Yang et al. (2019)**. The RoBERTa model also established a **new state-of-the-art on 4/9 of the GLUE tasks**. Despite these improvements, explicit **numerical comparison between BERT and RoBERTa's performance** on the GLUE and SQuAD benchmarks **is not provided** in the document.





