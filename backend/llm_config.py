import os


LLM_PROVIDER = "gemini"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
GEMINI_MAX_CONTEXT_CHARS = int(os.getenv("GEMINI_MAX_CONTEXT_CHARS", "8000"))

