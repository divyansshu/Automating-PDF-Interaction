"""
main.py
-------
FastAPI backend for the PDF Interaction application.
"""

import os
import shutil
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.pdf_processor import prepare_chunks_from_pdf
from backend.app.embeddings_generator import EmbeddingGenerator
from backend.app.vector_store import build_faiss_index, save_index, save_metadata, _FAISS_AVAILABLE
from backend.app.rag_pipeline import RAGPipeline

app = FastAPI(title="PDF Interaction API")

# CORS Setup (Allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG Pipeline instance
rag_pipeline = RAGPipeline()

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "PDF Interaction API is running."}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Uploads a PDF, processes it, and updates the vector store.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    # Save file locally
    file_location = f"uploaded_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Extract and Chunk
        print(f"Processing {file.filename}...")
        chunks = prepare_chunks_from_pdf(file_location)
        
        if not chunks:
             raise HTTPException(status_code=400, detail="No text extracted from PDF.")

        # 2. Generate Embeddings
        embedder = EmbeddingGenerator()
        embeddings_data = embedder.generate_embeddings(chunks)
        
        # 3. Update Vector Store
        # Prepare data for vector store
        import numpy as np
        vectors = np.stack([rec["embedding"] for rec in embeddings_data])
        metadata = [{
            "text": rec["text"],
            "page": rec["page"],
            "chunk_id": rec["chunk_id"],
            "source": file.filename
        } for rec in embeddings_data]

        # Save to disk
        if _FAISS_AVAILABLE:
            index = build_faiss_index(vectors)
            save_index(index)
        
        save_metadata(metadata)
        
        # Reload RAG pipeline with new data
        rag_pipeline.reload_index()
        
        # Cleanup
        os.remove(file_location)
        
        return {"message": "PDF processed and indexed successfully.", "chunks_count": len(chunks)}

    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_pdf(request: QueryRequest):
    """
    Answers a question based on the uploaded PDF.
    """
    if not rag_pipeline.index and not rag_pipeline.metadata:
        raise HTTPException(status_code=400, detail="No PDF indexed. Please upload a PDF first.")
    
    answer = rag_pipeline.answer_query(request.question)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
