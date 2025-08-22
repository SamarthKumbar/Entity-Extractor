from fastapi import FastAPI
from app.routes.upload import router as upload_router


app = FastAPI(title="Document Processing Pipeline")

app.include_router(upload_router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Document Pipeline is running"}
