from pathlib import Path

from embedding_config import EMBEDDING_MODEL
from embeddings import EmbeddingGenerator
from vector_config import VECTOR_DB
from vector_stores.chroma_store import ChromaVectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHROMA_DIR = PROJECT_ROOT / "artifacts" / "vector_db" / "chromadb" / "chroma"


class Retriever:
    def __init__(self, persist_dir=DEFAULT_CHROMA_DIR, top_k=5):
        if VECTOR_DB != "chromadb":
            raise ValueError(
                "Module 7 retrieval is configured for ChromaDB on main. "
                f"Current VECTOR_DB is {VECTOR_DB}."
            )

        self.top_k = top_k
        self.embedding_generator = EmbeddingGenerator(EMBEDDING_MODEL)
        self.vector_store = ChromaVectorStore(persist_dir=persist_dir)

    def retrieve(self, question, top_k=None):
        question = question.strip()

        if not question:
            raise ValueError("question cannot be empty.")

        top_k = top_k or self.top_k
        query_embeddings, query_seconds = self.embedding_generator.encode([question])
        results = self.vector_store.search(query_embeddings[0], top_k=top_k)

        return {
            "question": question,
            "top_k": top_k,
            "query_embedding_seconds": query_seconds,
            "results": results,
        }

