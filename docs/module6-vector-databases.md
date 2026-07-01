# Module 6: Vector Databases

This module compares storing website embeddings in two vector databases:

- `experiment/FAISS`
- `experiment/ChromaDB`

Both branches build on the MiniLM embedding workflow.

## Pipeline

```text
Website URL -> scrape -> preprocess -> chunk -> embedding -> vector DB -> retrieval
```

## Run FAISS

```powershell
git switch experiment/FAISS
pip install -r requirements.txt
python backend/benchmark_vector_store.py "https://stthomascollege.ac.in/" --query "What courses are offered?"
```

## Run ChromaDB

```powershell
git switch experiment/ChromaDB
pip install -r requirements.txt
python backend/benchmark_vector_store.py "https://stthomascollege.ac.in/" --query "What courses are offered?"
```

## Outputs

FAISS writes:

```text
artifacts/vector_db/faiss/faiss.index
artifacts/vector_db/faiss/faiss_chunks.json
artifacts/vector_db/faiss/vector_db_benchmark.json
```

ChromaDB writes:

```text
artifacts/vector_db/chromadb/chroma/
artifacts/vector_db/chromadb/vector_db_benchmark.json
```

## Merge decision

Compare:

- `index_seconds`
- `search_seconds`
- `top_results`
- setup complexity

FAISS is usually faster and lighter. ChromaDB is more feature-rich and easier for persistent collections.

