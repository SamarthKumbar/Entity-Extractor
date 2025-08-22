from pathlib import Path
from fastapi import UploadFile, HTTPException

def detect_file_type(file: UploadFile):
    ext = Path(file.filename).suffix.lower()
    if ext in [".docx"]:
        return "docx"
    elif ext in [".txt"]:
        return "txt"
    elif ext in [".pdf"]:
        return "pdf"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
