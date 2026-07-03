# Module 9: Groq API Experiment

This branch adds Groq response generation as a low-cost/free-tier-friendly LLM option.

## Flow

```text
Retrieved context + Question -> Groq -> Answer
```

## Environment

Do not commit API keys. Set the key locally:

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

Optional:

```powershell
$env:GROQ_MODEL="llama-3.3-70b-versatile"
$env:GROQ_TEMPERATURE="0.2"
$env:GROQ_MAX_CONTEXT_CHARS="8000"
```

## Run

Build the ChromaDB vector store first:

```powershell
python backend/benchmark_vector_store.py "https://stthomascollege.ac.in/" --query "What courses are offered?"
```

Generate an answer:

```powershell
python backend/answer_with_groq.py "What courses are offered?"
```

JSON output:

```powershell
python backend/answer_with_groq.py "What courses are offered?" --json
```

## API Key

Create a key from the Groq Console:

```text
https://console.groq.com/keys
```

Groq's official quickstart uses the `groq` Python package and `GROQ_API_KEY`.

