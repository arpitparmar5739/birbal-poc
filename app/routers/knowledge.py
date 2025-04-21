from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from embeddings.embedder import Embedder
from vectorstore.store_qdrant import QdrantStore
from typing import Optional

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

class AddKnowledgeRequest(BaseModel):
    text: str
    metadata: Optional[dict] = None

class AddKnowledgeResponse(BaseModel):
    success: bool
    message: str

class ClearKnowledgeResponse(BaseModel):
    success: bool
    message: str

# Initialize components
embedder = Embedder()
vector_store = QdrantStore()

def _format_metadata(metadata):
    """Format metadata into human-readable text"""
    formatted = []
    if metadata:
        # Add ticket ID first if it exists
        if 'ticket_id' in metadata:
            formatted.append(f"Ticket ID: {metadata['ticket_id']}")
            
        for k, v in metadata.items():
            if k != 'ticket_id':  # Skip ticket_id as it's already added
                key = k.replace('_', ' ').title()
                formatted.append(f"{key}: {v}")
    return "\n".join(formatted)

@router.post("/add", response_model=AddKnowledgeResponse)
async def add_knowledge(request: AddKnowledgeRequest):
    try:
        # Format metadata and content together
        metadata_text = _format_metadata(request.metadata)
        
        # Format text with ticket info
        formatted_text = f"Metadata:\n{metadata_text}\n\nContent:\n{request.text}"
        
        # Generate embedding
        embedding = embedder.embed([formatted_text])[0].tolist()
        
        # Ensure metadata fields are consistent
        metadata = {
            "ticket_id": request.metadata.get("ticket_id"),
            "category": request.metadata.get("category"),
            "priority": request.metadata.get("priority"),
            "status": request.metadata.get("status"),
            "platform": request.metadata.get("platform")
        } if request.metadata else {}
        
        # Clean None values
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        payload = {
            "formatted_text": formatted_text,
            **metadata  # Add metadata at root level for filtering
        }
        
        print(f"Storing payload: {payload}")  # Debug log
        vector_store.upsert([embedding], [payload])
        
        return AddKnowledgeResponse(success=True, message="Knowledge added successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear", response_model=ClearKnowledgeResponse)
async def clear_knowledge():
    try:
        success = vector_store.clear_data()
        return ClearKnowledgeResponse(
            success=success,
            message="Knowledge base cleared successfully" if success else "Failed to clear knowledge base"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))