from vector_config import VECTOR_DB


def create_vector_store(embedding_dimension, output_dir):
    if VECTOR_DB == "faiss":
        from vector_stores.faiss_store import FaissVectorStore

        return FaissVectorStore(dimension=embedding_dimension)

    if VECTOR_DB == "chromadb":
        from vector_stores.chroma_store import ChromaVectorStore

        return ChromaVectorStore(persist_dir=output_dir / "chroma")

    raise ValueError(f"Unsupported vector database: {VECTOR_DB}")

