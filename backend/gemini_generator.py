import os

from llm_config import GEMINI_MAX_CONTEXT_CHARS, GEMINI_MODEL, GEMINI_TEMPERATURE


GEMINI_PROMPT_TEMPLATE = """
You are a website question-answering assistant.
Use only the provided context to answer the question.
If the context does not contain the answer, say:
"I do not know based on the provided website content."

Context:
{context}

Question:
{question}

Answer:
""".strip()


class GeminiAnswerGenerator:
    def __init__(
        self,
        model_name=GEMINI_MODEL,
        temperature=GEMINI_TEMPERATURE,
        max_context_chars=GEMINI_MAX_CONTEXT_CHARS,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_context_chars = max_context_chars
        self.client = self._build_client()

    def _build_client(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if not api_key:
            return None

        try:
            from google import genai  # type: ignore[import]
            from google.genai import types  # type: ignore[import]
        except ImportError:
            return None

        return {
            "client": genai.Client(api_key=api_key),
            "types": types,
        }

    def generate(self, question, context):
        question = question.strip()
        context = (context or "").strip()[: self.max_context_chars]

        if not question:
            raise ValueError("question cannot be empty.")

        prompt = GEMINI_PROMPT_TEMPLATE.format(
            context=context or "No context was provided.",
            question=question,
        )

        if self.client is None:
            return {
                "answer": self._fallback_answer(context),
                "used_llm": False,
                "model": self.model_name,
                "temperature": self.temperature,
            }

        response = self.client["client"].models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.client["types"].GenerateContentConfig(
                temperature=self.temperature,
            ),
        )

        return {
            "answer": getattr(response, "text", "").strip(),
            "used_llm": True,
            "model": self.model_name,
            "temperature": self.temperature,
        }

    def _fallback_answer(self, context):
        if not context:
            return "I do not know based on the provided website content."

        return (
            "Gemini API credentials are not configured, so this is a retrieval-only "
            "fallback. Relevant context:\n\n"
            f"{context[:1200]}"
        )
