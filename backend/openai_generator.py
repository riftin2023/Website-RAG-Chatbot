import os

from llm_config import OPENAI_MAX_CONTEXT_CHARS, OPENAI_MODEL, OPENAI_TEMPERATURE


OPENAI_PROMPT_TEMPLATE = """
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


class OpenAIAnswerGenerator:
    def __init__(
        self,
        model_name=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
        max_context_chars=OPENAI_MAX_CONTEXT_CHARS,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_context_chars = max_context_chars
        self.client = self._build_client()

    def _build_client(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return None

        try:
            from openai import OpenAI  # type: ignore[import]
        except ImportError:
            return None

        return OpenAI(api_key=api_key)

    def generate(self, question, context):
        question = question.strip()
        context = (context or "").strip()[: self.max_context_chars]

        if not question:
            raise ValueError("question cannot be empty.")

        prompt = OPENAI_PROMPT_TEMPLATE.format(
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

        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[
                {
                    "role": "system",
                    "content": "Answer only using the provided website context.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        return {
            "answer": response.choices[0].message.content.strip(),
            "used_llm": True,
            "model": self.model_name,
            "temperature": self.temperature,
        }

    def _fallback_answer(self, context):
        if not context:
            return "I do not know based on the provided website content."

        return (
            "OpenAI API credentials are not configured, so this is a retrieval-only "
            "fallback. Relevant context:\n\n"
            f"{context[:1200]}"
        )

