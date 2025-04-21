# Knowledge Base Assistant PoC

This project implements a knowledge base assistant using the following architecture:

1. **Raw Data**: PDFs, DOCX, HTML, and TXT files are processed.
2. **Chunking and Embedding**: Documents are split into chunks and embedded using models like LangChain or SentenceTransformers.
3. **Vector Database**: Chunks are stored in a vector database (Qdrant, Chroma, or Pinecone).
4. **Query Handling**: User queries are embedded and matched with the most relevant chunks.
5. **LLM Integration**: Context and queries are sent to an LLM (e.g., OpenAI, Claude, LLaMA) for generating answers.

## Folder Structure

```
birbal-poc/
├── README.md
├── requirements.txt
├── .env                     # Store API keys here
├── data/
│   └── example_docs/        # Raw source files (PDFs, txt, etc.)
├── embeddings/
│   ├── embedder.py          # Code to embed documents
│   └── chunker.py           # Chunking logic
├── vectorstore/
│   ├── store_qdrant.py      # Vector DB initialization + upsert
│   └── retriever.py         # Search similar docs from Vector DB
├── llm/
│   └── query_llm.py         # Prompt LLM with retrieved context
├── app/
│   └── main.py              # Entry point: CLI or FastAPI app
├── utils/
│   └── loaders.py           # PDF, HTML, TXT loaders
└── config/
    └── settings.py          # Model/VDB config, environment variables
```

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add your API keys to the `.env` file.

3. Run the application:
   ```bash
   python app/main.py
   ```

## Quick Start

1. Create and populate `.env` file:
```bash
cp .env.example .env
# Add your OpenAI API key to .env file
OPENAI_API_KEY=your_key_here
```

2. Build and start the services:
```bash
docker-compose up --build
```

3. Test the API endpoints:

Add knowledge to the system:
```bash
curl -X POST "http://localhost:8000/knowledge/add" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Sample knowledge text",
           "metadata": {"source": "test"}
         }'
```

Query the knowledge base:
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
           "question": "What do you know about...?"
         }'
```

## Development

To run tests:
```bash
docker-compose exec app pytest
```

To check logs:
```bash
docker-compose logs -f
```

## Troubleshooting

1. If Qdrant fails to start, check its logs:
```bash
docker-compose logs qdrant
```

2. If you can't connect to the API, verify all services are running:
```bash
docker-compose ps
```
