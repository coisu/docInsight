import fitz  # PyMuPDF
import os
from typing import List

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a given PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def process_uploaded_pdfs(pdf_dir: str) -> List[dict]:
    """Processes all PDFs in the specified directory and extracts text."""
    extracted_data = []
    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, pdf_file)
            text = extract_text_from_pdf(pdf_path)
            extracted_data.append({"filename": pdf_file, "text": text})
    return extracted_data

if __name__ == "__main__":
    pdf_dir = "../data/pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    processed_data = process_uploaded_pdfs(pdf_dir)
    for entry in processed_data:
        print(f"Processed: {entry['filename']} - {len(entry['text'])} characters extracted.")
