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

## 📌 Future Enhancements
- **Accuracy Optimization**: Improve chunking, retrieval, and prompt engineering to provide more precise and context-aware answers.
- **Scalability**: Refactor the system to reliably support **large volumes of PDF files** without performance degradation.
- **Multi-language Support**: Enable semantic search and QA for documents in non-English languages.



## Result Examples

  #### uploaded file: WHO report for covid-19
  ![summarize](https://github.com/user-attachments/assets/88d99be1-c5ed-4c4c-8263-417491c950b6)
  ![summarize_answer](https://github.com/user-attachments/assets/abd64730-aa4b-42d3-9476-af1e5cf81ce8)


  #### uploaded file: Attention Is All You Need (* the paper that introduced the Transformer, showing that attention alone can replace RNNs for tasks like language translation.)

  ![원리질문](https://github.com/user-attachments/assets/2050e14b-2190-4731-a2a0-7407a6ce787b)
  ![논문단순질문과 대답](https://github.com/user-attachments/assets/ec15ffce-ce1b-4f9c-aae0-c84733e96f4d)
