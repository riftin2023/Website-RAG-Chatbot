# Module 9: Gemini API Response Generation

This module generates final RAG answers using Gemini.

## Flow

```text
Retrieved context + Question -> Gemini -> Answer
```

## Current Main Stack

- Embeddings: MiniLM
- Vector DB: ChromaDB
- Retrieval: Top 5 chunks
- LLM: Gemini

## Environment

Do not commit API keys. Set them locally:

```powershell
$env:GEMINI_API_KEY="your_gemini_api_key"
```

Optional:

```powershell
$env:GEMINI_MODEL="gemini-1.5-flash"
$env:GEMINI_TEMPERATURE="0.2"
$env:GEMINI_MAX_CONTEXT_CHARS="8000"
```

## Run

Build the vector DB first:

```powershell
python backend/benchmark_vector_store.py "https://stthomascollege.ac.in/" --query "What courses are offered?"
```

Generate an answer:

```powershell
python backend/answer_with_gemini.py "What courses are offered?"
```

JSON output:

```powershell
python backend/answer_with_gemini.py "What courses are offered?" --json
```

## Gemini vs OpenAI

Gemini is integrated on `main`.

Use this branch for the OpenAI experiment:

```text
experiment/OpenAI
```

Compare:

- answer quality
- faithfulness to retrieved context
- latency
- setup complexity
- cost/free-tier suitability

