import os


LLM_PROVIDER = "groq"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))
GROQ_MAX_CONTEXT_CHARS = int(os.getenv("GROQ_MAX_CONTEXT_CHARS", "8000"))

