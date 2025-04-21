# Code to initialize and upsert data into Qdrant vector database
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    PointStruct, 
    Distance, 
    VectorParams,
    OptimizersConfigDiff,
    HnswConfigDiff,
    CreateCollection
)
import os
import time
import uuid

class QdrantStore:
    def __init__(self, collection_name='kb_collection', vector_size=384):
        self.host = os.getenv('QDRANT_HOST', 'localhost')
        self.port = int(os.getenv('QDRANT_PORT', 6333))
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = QdrantClient(host=self.host, port=self.port)
        self.last_id = 0  # Track last used ID
        self._init_collection()
        self._init_last_id()

    def _init_collection(self):
        # Check if collection exists
        try:
            self.client.get_collection(self.collection_name)
        except:
            print(f"Creating new collection: {self.collection_name}")
            # Create collection with optimized settings
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                ),
                optimizers_config=OptimizersConfigDiff(
                    indexing_threshold=0,  # Index immediately
                    memmap_threshold=0  # Use memory mapping
                ),
                hnsw_config=HnswConfigDiff(
                    m=16,  # Number of connections per element
                    ef_construct=100,  # Build time quality factor
                    full_scan_threshold=10000  # When to switch to full scan
                )
            )
            print("Collection created with indexing enabled")

    def _init_last_id(self):
        """Initialize last_id based on existing points"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            self.last_id = collection_info.points_count or 0
            print(f"Initialized last_id to {self.last_id}")
        except Exception as e:
            print(f"Error initializing last_id: {e}")
            self.last_id = 0

    def upsert(self, embeddings, payloads):
        points = []
        for embedding, payload in zip(embeddings, payloads):
            point_id = self.last_id
            self.last_id += 1
            
            # Add ID to payload for tracking
            payload['point_id'] = str(point_id)
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            )
        
        self.client.upsert(collection_name=self.collection_name, points=points)
        print(f"Inserted {len(points)} points with IDs {[p.id for p in points]}")
        # Wait for indexing to complete
        self.client.update_collection(
            collection_name=self.collection_name,
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=0  # Force immediate indexing
            )
        )

    def delete_collection(self):
        """Delete the collection permanently"""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Collection {self.collection_name} deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")
            return False

    def clear_data(self):
        """Delete and recreate the collection to clear all data"""
        try:
            if self.delete_collection():
                self._init_collection()
                print(f"Collection {self.collection_name} recreated")
                return True
            return False
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False