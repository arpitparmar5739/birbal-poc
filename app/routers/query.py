from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from llm.query_llm import get_llm  # Updated import to get the factory function
from vectorstore.retriever import Retriever
from embeddings.embedder import Embedder
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

router = APIRouter(prefix="/query")  # Remove tags if not needed

class QueryRequest(BaseModel):
    question: str
    provider: Optional[str] = "together"
    model: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str

@router.post("")  # Empty string instead of "/"
async def query_kb(request: QueryRequest):
    try:
        # Initialize components
        retriever = Retriever()
        llm = get_llm(request.provider, request.model)
        embedder = Embedder()

        # Generate embedding for semantic search
        query_vector = embedder.embed([request.question])[0].tolist()
        
        # Get relevant documents with lower threshold
        context_results = retriever.retrieve(
            query_vector=query_vector,
            top_k=3,  # Get top 3 most relevant results
            score_threshold=0.3  # Lower threshold for better recall
        )
        
        if not context_results:
            return QueryResponse(answer="No relevant information found in the knowledge base.")

        # Join the pre-formatted texts with separators
        contexts = []
        for result in context_results:
            if result.get('text'):
                contexts.append(f"[Relevance: {result['score']:.2f}]\n{result['text']}")
        
        if not contexts:
            return QueryResponse(answer="Found results but no valid text content available.")
            
        context = "\n\n---\n\n".join(contexts)
        answer = llm.query(context, request.question)
        return QueryResponse(answer=answer)
            
    except Exception as e:
        print(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))