import os
import time
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from answer_with_groq import format_context
from chunking import TextChunker
from embedding_config import EMBEDDING_MODEL, MODEL_LABEL
from embeddings import EmbeddingGenerator
from groq_generator import GroqAnswerGenerator
from pipeline import RAGPipeline
from retriever import Retriever
from vector_config import VECTOR_DB, VECTOR_DB_LABEL
from vector_store_factory import create_vector_store


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VECTOR_OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "vector_db" / VECTOR_DB

app = Flask(__name__)
CORS(app)

current_website = {
    "url": "",
    "document_count": 0,
    "chunk_count": 0,
}


def get_request_data():
    return request.get_json(silent=True) or {}


def configure_groq_api_key(data):
    api_key = (data.get("api_key") or data.get("groq_api_key") or "").strip()

    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    return api_key or os.getenv("GROQ_API_KEY", "")


def summarize_sources(chunks, limit=5):
    sources = []

    for chunk in chunks[:limit]:
        sources.append(
            {
                "title": chunk.get("title", "Untitled"),
                "url": chunk.get("url", ""),
                "text": chunk.get("text", ""),
                "score": chunk.get("score"),
            }
        )

    return sources


@app.get("/")
def health_check():
    return jsonify(
        {
            "message": "Website RAG Chatbot API is running.",
            "endpoints": ["POST /crawl", "POST /chat"],
            "embedding_model": MODEL_LABEL,
            "vector_db": VECTOR_DB_LABEL,
            "active_url": current_website["url"],
        }
    )


@app.post("/crawl")
def crawl_website():
    started_at = time.perf_counter()
    data = get_request_data()
    url = (data.get("url") or "").strip()
    max_depth = int(data.get("max_depth") or 1)
    chunk_size = int(data.get("chunk_size") or 500)
    chunk_overlap = int(data.get("chunk_overlap") or 80)

    if not url:
        return jsonify({"error": "url is required."}), 400

    try:
        configure_groq_api_key(data)

        ingestion_pipeline = RAGPipeline(max_depth=max_depth)
        documents = ingestion_pipeline.ingest_website(url)

        if not documents:
            return jsonify({"error": "No pages were crawled from this website."}), 422

        chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks = chunker.chunk_documents(documents)

        if not chunks:
            return jsonify({"error": "No chunks were generated from this website."}), 422

        embedding_generator = EmbeddingGenerator(EMBEDDING_MODEL)
        texts = [chunk["text"] for chunk in chunks]
        embeddings, embedding_seconds = embedding_generator.encode(texts)

        VECTOR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        vector_store = create_vector_store(
            embedding_dimension=int(embeddings.shape[1]),
            output_dir=VECTOR_OUTPUT_DIR,
            reset=True,
        )
        vector_store.add(embeddings, chunks)
        vector_store.save(VECTOR_OUTPUT_DIR)

        current_website.update(
            {
                "url": url,
                "document_count": len(documents),
                "chunk_count": len(chunks),
            }
        )

        total_seconds = time.perf_counter() - started_at

        return jsonify(
            {
                "message": f"Ingested successfully ({len(documents)} pages, {len(chunks)} chunks)",
                "url": url,
                "document_count": len(documents),
                "chunk_count": len(chunks),
                "embedding_model": MODEL_LABEL,
                "vector_db": VECTOR_DB_LABEL,
                "embedding_seconds": embedding_seconds,
                "total_seconds": total_seconds,
                "sources": summarize_sources(chunks),
            }
        )
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.post("/chat")
def chat():
    data = get_request_data()
    question = (data.get("question") or "").strip()
    top_k = int(data.get("top_k") or 5)

    if not question:
        return jsonify({"error": "question is required."}), 400

    try:
        api_key = configure_groq_api_key(data)

        if not api_key:
            return jsonify({"error": "Groq API key is required."}), 400

        retriever = Retriever(top_k=top_k)
        retrieval = retriever.retrieve(question)
        context = format_context(retrieval["results"])

        generator = GroqAnswerGenerator()
        generation = generator.generate(question, context)

        return jsonify(
            {
                "question": question,
                "answer": generation["answer"],
                "used_llm": generation["used_llm"],
                "model": generation["model"],
                "temperature": generation["temperature"],
                "top_k": retrieval["top_k"],
                "query_embedding_seconds": retrieval["query_embedding_seconds"],
                "active_url": current_website["url"],
                "sources": summarize_sources(retrieval["results"], limit=top_k),
            }
        )
    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000, use_reloader=False)

