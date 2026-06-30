# Module 5: Embeddings

This module compares two embedding models for semantic search:

- `experiment/MiniLM`: `sentence-transformers/all-MiniLM-L6-v2`
- `experiment/BGE-Small`: `BAAI/bge-small-en-v1.5`

## Pipeline

```text
Website URL -> scrape documents -> preprocess text -> chunk text -> embeddings -> cosine similarity search
```

## Run

From the project root:

```powershell
python backend/benchmark_embeddings.py "https://example.com" --query "What is this website about?"
```

Or from `backend/`:

```powershell
python benchmark_embeddings.py "https://example.com" --query "What is this website about?"
```

## Outputs

The benchmark writes:

```text
artifacts/embeddings/document_embeddings.npy
artifacts/embeddings/chunks.json
artifacts/embeddings/embedding_benchmark.json
```

## Merge decision

Compare both branches using the same website and query. Choose the branch with:

- better top result relevance
- lower `document_embedding_seconds`
- lower `query_embedding_seconds`
- acceptable embedding dimension and memory usage

MiniLM is usually faster and lighter. BGE Small often gives stronger retrieval quality.

