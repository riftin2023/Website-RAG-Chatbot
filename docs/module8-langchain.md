# Module 8: LangChain RAG Pipeline

This module adds the answer-generation layer on top of retrieval.

## Flow

```text
Question -> Retriever -> Prompt -> LLM -> Answer with sources
```

## Current Stack

- Embeddings: MiniLM
- Vector DB: ChromaDB
- Retrieval: Top-k semantic search
- Prompt/chain layer: LangChain
- LLM: Gemini through LangChain when `GEMINI_API_KEY` or `GOOGLE_API_KEY` is configured

If no LLM key is configured, the pipeline returns a retrieval-only fallback answer using the top retrieved context.

## Prerequisite

Build the ChromaDB index first:

```powershell
python backend/benchmark_vector_store.py "https://stthomascollege.ac.in/" --query "What courses are offered?"
```

## Run

```powershell
python backend/rag_answer.py "What courses are offered?"
```

JSON output:

```powershell
python backend/rag_answer.py "What courses are offered?" --json
```

## Environment

Optional `.env` values:

```text
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-1.5-flash
```

## LangChain vs LlamaIndex

LangChain is integrated on `main`.

Use a separate branch for LlamaIndex:

```powershell
git switch -c experiment/llamaindex
```

Compare:

- pipeline code complexity
- retrieval quality
- prompt control
- integration effort
- runtime reliability

