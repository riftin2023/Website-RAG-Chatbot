import argparse
import json
from pathlib import Path

import numpy as np

from chunking import TextChunker
from embedding_config import EMBEDDING_MODEL, MODEL_LABEL
from embeddings import EmbeddingGenerator, top_k_similar
from pipeline import RAGPipeline


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Generate and benchmark website embeddings.")
    parser.add_argument("url", help="Website URL to scrape and embed.")
    parser.add_argument(
        "--query",
        default="What is this website about?",
        help="Query used for semantic search benchmarking.",
    )
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--chunk-overlap", type=int, default=80)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--output-dir",
        default="../artifacts/embeddings",
        help="Directory where embeddings and benchmark metadata are saved.",
    )
    return parser


def main():
    args = build_arg_parser().parse_args()

    pipeline = RAGPipeline(max_depth=args.max_depth)
    documents = pipeline.ingest_website(args.url)

    chunker = TextChunker(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    chunks = chunker.chunk_documents(documents)

    if not chunks:
        print("No chunks generated. Check the URL or scraper output.")
        return

    generator = EmbeddingGenerator(EMBEDDING_MODEL)
    texts = [chunk["text"] for chunk in chunks]

    embeddings, embedding_seconds = generator.generate_embeddings(texts)
    query_embedding, query_seconds = generator.generate_embeddings([args.query])
    results = top_k_similar(query_embedding[0], embeddings, chunks, k=args.top_k)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    np.save(output_dir / "document_embeddings.npy", embeddings)

    metadata = {
        "model_label": MODEL_LABEL,
        "model_name": EMBEDDING_MODEL,
        "url": args.url,
        "query": args.query,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "embedding_seconds": embedding_seconds,
        "query_seconds": query_seconds,
        "embedding_dimension": int(embeddings.shape[1]),
        "top_results": results,
    }

    metadata_path = output_dir / "embedding_benchmark.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("\n========== EMBEDDING BENCHMARK ==========")
    print(f"Model       : {MODEL_LABEL}")
    print(f"Model name  : {EMBEDDING_MODEL}")
    print(f"Documents   : {len(documents)}")
    print(f"Chunks      : {len(chunks)}")
    print(f"Dimensions  : {embeddings.shape[1]}")
    print(f"Embed time  : {embedding_seconds:.2f}s")
    print(f"Query time  : {query_seconds:.4f}s")
    print(f"Saved report: {metadata_path}")

    print("\nTop results:")
    for index, result in enumerate(results, start=1):
        print(f"\n{index}. {result['title']} ({result['score']:.4f})")
        print(result["url"])
        print(result["text"][:300])


if __name__ == "__main__":
    main()

