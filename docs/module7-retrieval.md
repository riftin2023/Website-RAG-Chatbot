# Module 7: Retrieval

This module builds the RAG search engine.

## Goal

```text
Question -> MiniLM embedding -> ChromaDB search -> Top 5 chunks
```

## Technique

The retrieval method is dense semantic search:

- embed the user question with MiniLM
- search the persisted ChromaDB collection
- return the top-k most similar chunks

## Prerequisite

Build the ChromaDB vector store first:

```powershell
python backend/benchmark_vector_store.py "https://stthomascollege.ac.in/" --query "What courses are offered?"
```

## Run Retrieval

```powershell
python backend/retrieve.py "What courses are offered?"
```

Return JSON:

```powershell
python backend/retrieve.py "What courses are offered?" --json
```

Change top-k:

```powershell
python backend/retrieve.py "What courses are offered?" --top-k 5
```

## Output

The retriever returns:

- user question
- query embedding time
- top-k chunks
- chunk score
- source URL
- chunk text

