# Semantic Search + LLM Project

## 📌 Project Overview
This project is designed to process uploaded PDF documents and perform **semantic search** using **Large Language Models (LLM)** to generate optimal answers. Instead of simple keyword matching, it employs **semantic similarity-based document retrieval** combined with **LLM-generated structured responses**.

## 🎯 Project Objectives
- Enable users to quickly find relevant information through **semantic search**.
- Provide **LLM-powered summarization** of retrieved documents for coherent and logical answers.
- Develop a **browser-accessible web interface** for seamless user interaction.
- Utilize **Docker for containerized deployment** to ensure easy setup and execution.

## ⚡ Key Features
### ✅ PDF Upload & Preprocessing
- Users can upload PDF documents, which are then **processed for text extraction**.
- Extracted text is **embedded into vector representations** and stored in **FAISS/ChromaDB**.

### ✅ Semantic Search (Vector-based Retrieval)
- Converts user queries into vector embeddings to **find the most semantically similar document snippets**.
- Scores and ranks retrieved results based on relevance.

### ✅ LLM-based Answer Generation
- Retrieves relevant document snippets and **passes them to LLM for summarization**.
- Ensures **coherent and structured responses** beyond simple keyword matching.

### ✅ Browser-based UI
- Provides a **user-friendly interface** for query input, search results, and document management.
- Built with **Streamlit or React**.

## 🔧 Tech Stack
| Component | Technology |
|------------|-------------|
| **Backend API** | FastAPI (Python) |
| **Frontend** | Streamlit or React |
| **Vector Store** | FAISS or ChromaDB |
| **Embedding Model** | Sentence Transformers (`all-mpnet-base-v2`) |
| **LLM Engine** | GPT-4, Claude, Llama3 |
| **Containerization** | Docker, Docker Compose |
| **Build & Deployment** | Makefile |
| **PDF Processing** | PyMuPDF, pdfminer.six |

## 📊 Data Flow
```
1️⃣ User inputs a query via the web interface
      ↓
2️⃣ Query is embedded using Sentence Transformers
      ↓
3️⃣ FAISS or ChromaDB searches for semantically similar document snippets
      ↓
4️⃣ Retrieved documents are scored and ranked for relevance
      ↓
5️⃣ LLM constructs a response using the retrieved context
      ↓
6️⃣ LLM generates a structured summary and answer
      ↓
7️⃣ The response is displayed in the web interface
```

## 🚀 Development & Execution
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/coisu/semantic-search-llm.git
cd semantic-search-llm
```

### 2️⃣ Run the Docker Containers
```bash
make build
make run
```

### 3️⃣ Access the Web Interface
```
http://localhost:8501  (Streamlit UI)
http://localhost:8000/docs  (FastAPI Swagger UI)
```

## 📌 Future Enhancements
- 🔄 Optimize LLM inference speed and implement caching
- 🔎 Add similar document recommendations
- 📄 Extend OCR functionality for scanned PDFs
