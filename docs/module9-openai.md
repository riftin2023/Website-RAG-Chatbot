# Module 9: OpenAI API Experiment

This branch compares OpenAI response generation against Gemini.

## Flow

```text
Retrieved context + Question -> OpenAI -> Answer
```

## Environment

Do not commit API keys. Set them locally:

```powershell
$env:OPENAI_API_KEY="your_openai_api_key"
```

Optional:

```powershell
$env:OPENAI_MODEL="gpt-4o-mini"
$env:OPENAI_TEMPERATURE="0.2"
```

## Run

```powershell
python backend/answer_with_openai.py "What courses are offered?"
```

