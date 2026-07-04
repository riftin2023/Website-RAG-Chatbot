import os
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
from flask import Flask, jsonify, request
from flask_cors import CORS

from chunking import TextChunker
from embedding_config import EMBEDDING_MODEL
from embeddings import EmbeddingGenerator
from groq_generator import GroqAnswerGenerator
from pipeline import RAGPipeline
from vector_config import VECTOR_DB
from vector_store_factory import create_vector_store
from full_rag_pipeline import format_context, DEFAULT_OUTPUT_DIR

app = Flask(__name__)
CORS(app)


@app.get("/")
def health_check():
    return jsonify(
        {
            "message": "Website RAG Chatbot API is running.",
            "endpoints": ["POST /crawl", "POST /chat"],
        }
    )


@app.post("/crawl")
def crawl_website():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "url is required."}), 400

    try:
        # Ingestion
        ingestion_pipeline = RAGPipeline(max_depth=1)
        documents = ingestion_pipeline.ingest_website(url)

        # Chunking
        chunker = TextChunker(chunk_size=500, chunk_overlap=80)
        chunks = chunker.chunk_documents(documents)

        if not chunks:
            return jsonify({"error": "No content could be extracted from the website."}), 400

        # Embeddings
        embedding_generator = EmbeddingGenerator(EMBEDDING_MODEL)
        texts = [chunk["text"] for chunk in chunks]
        embeddings, embedding_seconds = embedding_generator.encode(texts)

        # Vector Store Creation
        vector_output_dir = Path(DEFAULT_OUTPUT_DIR) / VECTOR_DB
        vector_output_dir.mkdir(parents=True, exist_ok=True)

        vector_store = create_vector_store(
            embedding_dimension=int(embeddings.shape[1]),
            output_dir=vector_output_dir,
            reset=True,
        )
        vector_store.add(embeddings, chunks)
        vector_store.save(vector_output_dir)

        return jsonify(
            {
                "message": "Website successfully ingested and indexed.",
                "url": url,
                "document_count": len(documents),
                "chunk_count": len(chunks),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    api_key = (data.get("api_key") or "").strip()

    if not question:
        return jsonify({"error": "question is required."}), 400

    try:
        vector_output_dir = Path(DEFAULT_OUTPUT_DIR) / VECTOR_DB
        if not vector_output_dir.exists():
            return jsonify({"error": "No website has been crawled yet. Please crawl a website first."}), 400

        # Embed question
        embedding_generator = EmbeddingGenerator(EMBEDDING_MODEL)
        query_embeddings, _ = embedding_generator.encode([question])

        # Load vector store (without reset)
        vector_store = create_vector_store(
            embedding_dimension=int(query_embeddings.shape[1]),
            output_dir=vector_output_dir,
            reset=False,
        )

        # Search
        top_k = 5
        retrieved_chunks = vector_store.search(query_embeddings[0], top_k=top_k)
        context = format_context(retrieved_chunks)

        # Generate answer
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key

        answer_generator = GroqAnswerGenerator()
        generation = answer_generator.generate(question, context)

        return jsonify(
            {
                "message": "Answer generated successfully.",
                "question": question,
                "answer": generation["answer"],
                "used_llm": generation["used_llm"],
                "sources": retrieved_chunks,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000, use_reloader=False)

