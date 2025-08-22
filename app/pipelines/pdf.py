import pdfplumber
from typing import List, Dict
from langchain.vectorstores import FAISS as LangchainFAISS
from langchain.embeddings import HuggingFaceEmbeddings
from openai import OpenAI
import os
import json
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(
    api_key="API_KEY_FOR_LLM",  
    base_url="https://api.groq.com/openai/v1"
)


CHUNK_SIZE = 500  
TOP_K = 3         


def pdf_to_text(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def build_vectorstore(chunks: List[str]) -> LangchainFAISS:
    hf_embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = LangchainFAISS.from_texts(chunks, hf_embeddings)
    return vectorstore


def run_rag_extraction(vectorstore: LangchainFAISS, user_question: str) -> str:
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": TOP_K})
    
    
    relevant_chunks = retriever.get_relevant_documents(user_question)
    text_for_model = "\n\n".join([doc.page_content for doc in relevant_chunks])

    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_question + "\n\nContext:\n" + text_for_model}],
            temperature=0
        )
        output = response.choices[0].message.content
        return output
    except Exception as e:
        return f"Groq LLM request failed: {e}"

def run_pdf(pdf_path: str) -> LangchainFAISS:
    """
    Creates embeddings for the PDF and returns the vectorstore
    """
    text = pdf_to_text(pdf_path)
    chunks = chunk_text(text)
    vectorstore = build_vectorstore(chunks)
    return vectorstore


class PDFChat:
    def __init__(self, pdf_path: str):
        self.vectorstore = run_pdf(pdf_path)

    def ask(self, question: str) -> str:
        answer = run_rag_extraction(self.vectorstore, question)
        return answer
