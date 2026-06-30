import argparse
import json
from pathlib import Path

import numpy as np

from chunking import TextChunker
from embedding_config import EMBEDDING_MODEL, MODEL_LABEL
from embeddings import EmbeddingGenerator, semantic_search
from pipeline import RAGPipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "embeddings"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Scrape a website, chunk documents, generate embeddings, and run cosine similarity search."
    )
    parser.add_argument("url", help="Website URL to scrape.")
    parser.add_argument(
        "--query",
        default="What is this website about?",
        help="Question used to test semantic search.",
    )
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--chunk-overlap", type=int, default=80)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Folder where embeddings and benchmark JSON are saved.",
    )
    return parser


def save_outputs(output_dir, embeddings, chunks, report):
    output_dir.mkdir(parents=True, exist_ok=True)

    np.save(output_dir / "document_embeddings.npy", embeddings)
    (output_dir / "chunks.json").write_text(
        json.dumps(chunks, indent=2),
        encoding="utf-8",
    )
    (output_dir / "embedding_benchmark.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )


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
    embeddings, document_embedding_seconds = generator.encode(texts)
    query_embeddings, query_embedding_seconds = generator.encode([args.query])

    top_results = semantic_search(
        query_embedding=query_embeddings[0],
        document_embeddings=embeddings,
        chunks=chunks,
        top_k=args.top_k,
    )

    report = {
        "model_label": MODEL_LABEL,
        "model_name": EMBEDDING_MODEL,
        "url": args.url,
        "query": args.query,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "embedding_dimension": int(embeddings.shape[1]),
        "document_embedding_seconds": document_embedding_seconds,
        "query_embedding_seconds": query_embedding_seconds,
        "top_results": top_results,
    }

    output_dir = Path(args.output_dir).resolve()
    save_outputs(output_dir, embeddings, chunks, report)

    print("\n========== MODULE 5 EMBEDDING BENCHMARK ==========")
    print(f"Model       : {MODEL_LABEL}")
    print(f"Model name  : {EMBEDDING_MODEL}")
    print(f"Documents   : {len(documents)}")
    print(f"Chunks      : {len(chunks)}")
    print(f"Dimensions  : {embeddings.shape[1]}")
    print(f"Embed time  : {document_embedding_seconds:.2f}s")
    print(f"Query time  : {query_embedding_seconds:.4f}s")
    print(f"Output dir  : {output_dir}")

    print("\nTop semantic matches:")
    for index, result in enumerate(top_results, start=1):
        print(f"\n{index}. {result['title']} | score={result['score']:.4f}")
        print(result["url"])
        print(result["text"][:300])


if __name__ == "__main__":
    main()

