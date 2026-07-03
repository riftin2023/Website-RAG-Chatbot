# Module 10: Full RAG Pipeline

This module runs the complete selected RAG system.

## Final Main Stack

- Scraper: BeautifulSoup
- Preprocessing: custom text cleaner
- Chunking: fixed-size overlapping chunks
- Embeddings: MiniLM
- Vector DB: ChromaDB
- Retrieval: top-k semantic search
- LLM: Groq

## Flow

```text
Website -> Scraper -> Preprocess -> Chunk -> Embed -> ChromaDB -> Retrieve -> Groq -> Answer
```

## Environment

Set your Groq key locally:

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

Optional:

```powershell
$env:GROQ_MODEL="llama-3.3-70b-versatile"
$env:GROQ_TEMPERATURE="0.2"
```

## Run

```powershell
python backend/full_rag_pipeline.py "https://stthomascollege.ac.in/" "What courses are offered?"
```

JSON output:

```powershell
python backend/full_rag_pipeline.py "https://stthomascollege.ac.in/" "What courses are offered?" --json
```

## Output

The command writes:

```text
artifacts/full_rag/full_rag_result.json
```

It also stores vector artifacts under:

```text
artifacts/full_rag/chromadb/
```

