from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from embeddings.embedder import Embedder

router = APIRouter(prefix="/embedding", tags=["embedding"])

class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embedding: List[float]

# Initialize embedder
embedder = Embedder()

@router.post("/", response_model=EmbeddingResponse)
async def create_embedding(request: EmbeddingRequest):
    try:
        # Generate embedding using sentence transformers
        embedding = embedder.embed([request.text])[0].tolist()
        return EmbeddingResponse(embedding=embedding)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))