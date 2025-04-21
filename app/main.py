# Entry point for the application
from app import create_app
from utils.data_loader import DataLoader
from pathlib import Path

app = create_app()
data_loader = DataLoader()

@app.on_event("startup")
async def load_initial_data():
    print("Starting data initialization...")
    try:
        # Clear existing data
        print("Clearing existing knowledge base...")
        data_loader.vector_store.clear_data()
        print("Knowledge base cleared")
        
        # Load new data
        print("Loading initial knowledge base data...")
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / 'scripts' / 'data'
        
        all_data = data_loader.load_json_files(data_dir)
        print(f"Found {len(all_data)} entries")
        
        await data_loader.process_entries(all_data)
        print("Initial data loading complete!")
    except Exception as e:
        print(f"Error during initial data load: {str(e)}")
