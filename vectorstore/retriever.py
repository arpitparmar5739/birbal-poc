from qdrant_client import QdrantClient
import os

class Retriever:
    """Retrieves similar documents from Qdrant vector database."""
    
    def __init__(self, collection_name='kb_collection'):
        self.host = os.getenv('QDRANT_HOST', 'localhost')
        self.port = int(os.getenv('QDRANT_PORT', 6333))
        self.collection_name = collection_name
        self.client = QdrantClient(host=self.host, port=self.port)

    def retrieve(self, query_vector, top_k=5, score_threshold=0.1, with_payload=True):
        """Lowered score threshold for better recall"""
        try:
            print(f"Searching with query vector of length: {len(query_vector)}")
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=with_payload
            )

            print(f"Found {len(results)} results")
            formatted_results = []
            for r in results:
                payload = r.payload or {}
                text = payload.get('formatted_text', '')
                print(f"Score: {r.score:.3f}, Text preview: {text[:100]}...")
                formatted_results.append({
                    'text': text,
                    'score': r.score,
                    'metadata': {k:v for k,v in payload.items() if k not in ['formatted_text', 'raw_text']}
                })
                    
            return formatted_results

        except Exception as e:
            print(f"Retrieval error: {str(e)}")
            return []