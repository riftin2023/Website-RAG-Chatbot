import argparse
import json
import time
from pathlib import Path

import numpy as np

from chunking import TextChunker
from embedding_config import EMBEDDING_MODEL, MODEL_LABEL
from embeddings import EmbeddingGenerator
from pipeline import RAGPipeline
from vector_config import VECTOR_DB, VECTOR_DB_LABEL
from vector_store_factory import create_vector_store


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "vector_db"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Store website embeddings in a vector database and benchmark retrieval."
    )
    parser.add_argument("url", help="Website URL to scrape.")
    parser.add_argument(
        "--query",
        default="What is this website about?",
        help="Question used to test vector search.",
    )
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--chunk-overlap", type=int, default=80)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Folder where vector DB artifacts and benchmark JSON are saved.",
    )
    return parser


def main():
    args = build_parser().parse_args()

    pipeline = RAGPipeline(max_depth=args.max_depth)
    documents = pipeline.ingest_website(args.url)

    chunker = TextChunker(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    chunks = chunker.chunk_documents(documents)

    if not chunks:
        raise RuntimeError("No chunks were generated. Check the URL or scraper output.")

    generator = EmbeddingGenerator(EMBEDDING_MODEL)
    texts = [chunk["text"] for chunk in chunks]

    embeddings, embedding_seconds = generator.encode(texts)
    query_embeddings, query_embedding_seconds = generator.encode([args.query])

    output_dir = Path(args.output_dir).resolve() / VECTOR_DB
    output_dir.mkdir(parents=True, exist_ok=True)

    store = create_vector_store(
        embedding_dimension=int(embeddings.shape[1]),
        output_dir=output_dir,
    )

    index_started_at = time.perf_counter()
    store.add(embeddings, chunks)
    index_seconds = time.perf_counter() - index_started_at

    search_started_at = time.perf_counter()
    top_results = store.search(query_embeddings[0], top_k=args.top_k)
    search_seconds = time.perf_counter() - search_started_at

    store.save(output_dir)
    np.save(output_dir / "document_embeddings.npy", embeddings)

    report = {
        "vector_db": VECTOR_DB,
        "vector_db_label": VECTOR_DB_LABEL,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_model_label": MODEL_LABEL,
        "url": args.url,
        "query": args.query,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "embedding_dimension": int(embeddings.shape[1]),
        "embedding_seconds": embedding_seconds,
        "query_embedding_seconds": query_embedding_seconds,
        "index_seconds": index_seconds,
        "search_seconds": search_seconds,
        "top_results": top_results,
    }

    report_path = output_dir / "vector_db_benchmark.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n========== MODULE 6 VECTOR DB BENCHMARK ==========")
    print(f"Vector DB   : {VECTOR_DB_LABEL}")
    print(f"Embedding   : {MODEL_LABEL}")
    print(f"Documents   : {len(documents)}")
    print(f"Chunks      : {len(chunks)}")
    print(f"Dimensions  : {embeddings.shape[1]}")
    print(f"Embed time  : {embedding_seconds:.2f}s")
    print(f"Index time  : {index_seconds:.4f}s")
    print(f"Search time : {search_seconds:.4f}s")
    print(f"Output dir  : {output_dir}")

    print("\nTop vector matches:")
    for index, result in enumerate(top_results, start=1):
        print(f"\n{index}. {result.get('title', 'Untitled')} | score={result.get('score', 0):.4f}")
        print(result.get("url", ""))
        print(result.get("text", "")[:300])


if __name__ == "__main__":
    main()

