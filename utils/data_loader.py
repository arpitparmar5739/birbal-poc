import json
from pathlib import Path
from embeddings.embedder import Embedder
from vectorstore.store_qdrant import QdrantStore
import asyncio

class DataLoader:
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = QdrantStore()

    def load_json_files(self, data_dir):
        data_path = Path(data_dir)
        all_data = []
        for json_file in data_path.glob('*.json'):
            with open(json_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        return all_data

    async def process_entries(self, entries):
        for entry in entries:
            try:
                text = entry['text']
                embedding = self.embedder.embed([text])[0].tolist()
                self.vector_store.upsert([embedding], [entry])
                
                identifier = entry.get('metadata', {}).get('ticket_id') or \
                           entry.get('metadata', {}).get('category', 'unknown')
                print(f"Added entry: {identifier}")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error processing entry: {str(e)}")
