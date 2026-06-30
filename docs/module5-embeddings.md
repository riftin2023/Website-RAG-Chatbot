# Module 5: Embeddings

Goal: understand semantic search by converting website chunks into vectors and comparing embedding models.

## Flow

```text
Website documents -> chunks -> embeddings -> cosine similarity search
```

## Experiment branches

- `experiment/MiniLM`
- `experiment/BGE-Small`

Both branches use the same code. Only `backend/embedding_config.py` changes.

## Run benchmark

From `backend/`:

```powershell
python benchmark_embeddings.py "https://example.com" --query "What does this website explain?"
```

The script saves:

```text
artifacts/embeddings/document_embeddings.npy
artifacts/embeddings/embedding_benchmark.json
```

## Compare

Use these metrics:

- `embedding_seconds`: lower is faster
- `query_seconds`: lower is faster
- `chunk_count`: should be the same for both branches
- `top_results`: manually inspect relevance
- `embedding_dimension`: smaller is usually cheaper

Merge the branch that gives the best relevance with acceptable speed.

