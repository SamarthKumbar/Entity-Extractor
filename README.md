# Financial Document Entity Extractor

A FastAPI + Streamlit application that extracts entities from financial documents (`PDF`, `TXT`, `DOCX`) and provides a chat interface for PDFs using a Retrieval-Augmented Generation (RAG) approach.

---

## Features

- **Multi-format support**: `.pdf`, `.txt`, `.docx`  
- **Entity Extraction**: Counterparty, Date, Notional, Underlying, PaymentFrequency, Coupon/Spread, ISIN  
- **RAG Chat for PDFs**: Ask questions dynamically about uploaded PDF content  
- **Backend**: FastAPI  
- **Frontend**: Streamlit  
- **Embeddings**: HuggingFace Sentence Transformers  
- **LLM**: Groq-compatible `llama-3.3-70b-versatile`  

---

## Project Structure

├── app/
│ ├── api/ # FastAPI endpoints
│ ├── pipelines/ # Extraction pipelines (PDF, NER, Regex)
│ └── utils/ # Utility functions (file type detection, etc.)
├── frontend/ # Streamlit app
├── venv/ # Virtual environment (ignored in git)
├── .env # API keys (ignored in git)
├── main.py # FastAPI main file
├── requirements.txt # Python dependencies
└── README.md

yaml
Copy
Edit

---

## Installation

1. Clone the repo:

```bash
git clone https://github.com/your-username/financial-doc-extractor.git
cd financial-doc-extractor
Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt

Create a .env file with your Groq/OpenAI API key:

API_KEY=your_api_key_here
Running the Backend

uvicorn main:app --reload --port 8001
Upload files: POST /api/upload

Ask questions for PDFs: POST /api/ask_pdf

Running the Frontend

streamlit run frontend/app.py
Upload your financial document

If PDF, ask questions dynamically in the chat interface

```
