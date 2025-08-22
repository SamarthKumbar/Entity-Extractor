from fastapi import APIRouter, UploadFile, File
import tempfile
from app.utils.file import detect_file_type
from app.pipelines.regex import run_regex
from app.pipelines.ner import run_ner
from app.pipelines.pdf import run_pdf, PDFChat 
import uuid


router = APIRouter()

pdf_chats = {}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    
    file_type = detect_file_type(file)

    
    if file_type == "docx":
        result = run_regex(file)

    
    elif file_type == "txt":
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")
        result = run_ner(text_content=text_content)

    
    elif file_type == "pdf":
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        
        result = run_pdf(tmp_path)

       
        pdf_id = str(uuid.uuid4())
        chat_instance = PDFChat(tmp_path)
        pdf_chats[pdf_id] = chat_instance 

        return {"file_type": file_type, "result": "Embeddings created successfully", "pdf_id": pdf_id}

    else:
        return {"error": "Unsupported file type"}

    return {"file_type": file_type, "result": result}


@router.post("/ask_pdf")
async def ask_pdf(pdf_id: str, question: str):
    if pdf_id not in pdf_chats:
        return {"error": "Invalid PDF ID or PDF not uploaded"}

    chat_instance = pdf_chats[pdf_id]
    answer = chat_instance.ask(question)
    return {"question": question, "answer": answer}
