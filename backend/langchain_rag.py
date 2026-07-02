import os
from pathlib import Path

from retriever import DEFAULT_CHROMA_DIR, Retriever

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate
    from langchain_core.runnables import RunnableLambda
except ImportError:
    StrOutputParser = None
    PromptTemplate = None
    RunnableLambda = None


if load_dotenv:
    load_dotenv()


RAG_PROMPT_TEMPLATE = """
You are a website question-answering assistant.
Answer the question using only the context below.
If the answer is not present in the context, say: "I do not know based on the provided website content."

Context:
{context}

Question:
{question}

Answer:
""".strip()


class LangChainRAGPipeline:
    def __init__(self, persist_dir=DEFAULT_CHROMA_DIR, top_k=5):
        self.retriever = Retriever(
            persist_dir=Path(persist_dir),
            top_k=top_k,
        )
        self.top_k = top_k
        self.llm = self._build_llm()
        self.chain = self._build_chain()

    def _build_llm(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if not api_key:
            return None

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            return None

        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            google_api_key=api_key,
            temperature=0,
        )

    def _build_chain(self):
        if PromptTemplate is None or RunnableLambda is None:
            return None

        prompt = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

        if self.llm is None:
            return prompt | RunnableLambda(self._fallback_answer)

        if StrOutputParser is None:
            return prompt | self.llm

        return prompt | self.llm | StrOutputParser()

    def ask(self, question, top_k=None):
        retrieval = self.retriever.retrieve(question, top_k=top_k or self.top_k)
        context = self._format_context(retrieval["results"])

        inputs = {
            "question": question,
            "context": context,
        }

        if self.chain is None:
            answer = self._fallback_answer(inputs)
        else:
            answer = self.chain.invoke(inputs)

        return {
            "question": question,
            "answer": str(answer).strip(),
            "top_k": retrieval["top_k"],
            "query_embedding_seconds": retrieval["query_embedding_seconds"],
            "sources": self._format_sources(retrieval["results"]),
            "chunks": retrieval["results"],
            "used_llm": self.llm is not None,
        }

    def _format_context(self, chunks):
        if not chunks:
            return "No relevant context was retrieved."

        context_blocks = []

        for index, chunk in enumerate(chunks, start=1):
            context_blocks.append(
                "\n".join(
                    [
                        f"[Chunk {index}]",
                        f"Title: {chunk.get('title', 'Untitled')}",
                        f"URL: {chunk.get('url', '')}",
                        f"Content: {chunk.get('text', '')}",
                    ]
                )
            )

        return "\n\n".join(context_blocks)

    def _format_sources(self, chunks):
        sources = []

        for chunk in chunks:
            source = {
                "title": chunk.get("title", "Untitled"),
                "url": chunk.get("url", ""),
                "score": chunk.get("score"),
            }

            if source not in sources:
                sources.append(source)

        return sources

    def _fallback_answer(self, inputs):
        context = inputs.get("context", "").strip()

        if not context or context == "No relevant context was retrieved.":
            return "I do not know based on the provided website content."

        return (
            "LLM credentials are not configured, so this is a retrieval-only answer. "
            "The most relevant website context is:\n\n"
            f"{context[:1200]}"
        )

