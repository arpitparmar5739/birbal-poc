from fastapi import FastAPI
from app.routers import query, embedding, knowledge

def create_app() -> FastAPI:
    app = FastAPI()
    # Include routers
    app.include_router(query.router)
    app.include_router(embedding.router)
    app.include_router(knowledge.router)
    return app
