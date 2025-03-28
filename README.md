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

- [ ] 🚧 **Prompt Engineering & Context Selection Optimization**  
  Improve retrieval precision and summarization quality by:  
  - controlling prompt length  
  - combining keyword-based and vector-based chunk selection  
  - exploring highlight-based chunk prioritization

- [ ] 🚧 **Robust Handling of Multi-Document Reasoning**  
  Continue testing complex multi-file questions, especially those requiring reasoning across 2 or 3 specific documents.  
  → Includes indirect, comparison, and hybrid question types for reliability testing.

- [ ] 🚧 **Scalability for Large Document Sets**  
  Optimize indexing, chunking, and memory usage to support 50+ PDF documents without performance degradation.  
  → Refactor chunk loading, vector storage, and file filtering pipeline.

- [ ]  **Improved Frontend UI/UX**  
  Refine document selection interface (multi-select dropdown, file chunk preview) and show per-query type indicators (`summary`, `comparison`, `normal`).

- [ ]  **Multi-language Support**  
  Extend semantic search and question answering to non-English documents, starting with Korean and French support.

- [ ]  **Debugging & Explainability Tools**  
  Add developer-facing tools to log and visualize:  
  - selected chunks and similarity scores  
  - how each chunk contributed to the answer  
  - query classification reasoning (e.g., cosine similarity value)


-------------------

### 📌 Result Generator Development

> Currently supporting multi-document queries with dynamic answer generation based on query type.  
> The query type is determined using `classify_query_sementic()` in `embeddings.py`.

---
#### Uploaded Files
- `RoBERTa.pdf`
- `language_understanding_paper.pdf`
- `1810.04805v2.pdf`

  #### Question
> *"Help me understand the general direction of these documents."*

This query is intentionally designed to **avoid direct keywords** such as “summarize” or “compare” to test whether the semantic embedding-based classification works correctly.

---
### ✅ Result
> This workflow demonstrates that the system can semantically understand the intent of natural queries and dynamically generate contextualized answers based on multiple documents.

As shown in the following screenshots:
  - The system correctly classified the query as a **`summary`** type.
  - It returned individual summaries for each uploaded document.
  - Each summary section includes a toggle to view the **original document chunks** used to generate the response.

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


-------------------------------------------------------
