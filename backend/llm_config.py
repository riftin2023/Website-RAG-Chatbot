import os


LLM_PROVIDER = "openai"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
OPENAI_MAX_CONTEXT_CHARS = int(os.getenv("OPENAI_MAX_CONTEXT_CHARS", "8000"))

