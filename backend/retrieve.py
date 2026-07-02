import argparse
import json
from pathlib import Path

from retriever import DEFAULT_CHROMA_DIR, Retriever


def build_parser():
    parser = argparse.ArgumentParser(
        description="Retrieve top-k chunks from ChromaDB for a user question."
    )
    parser.add_argument("question", help="Question to search for.")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--persist-dir",
        default=str(DEFAULT_CHROMA_DIR),
        help="ChromaDB persistence directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full retrieval output as JSON.",
    )
    return parser


def main():
    args = build_parser().parse_args()

    retriever = Retriever(
        persist_dir=Path(args.persist_dir),
        top_k=args.top_k,
    )
    output = retriever.retrieve(args.question)

    if args.json:
        print(json.dumps(output, indent=2))
        return

    print("\n========== MODULE 7 RETRIEVAL ==========")
    print(f"Question    : {output['question']}")
    print(f"Top K       : {output['top_k']}")
    print(f"Query time  : {output['query_embedding_seconds']:.4f}s")

    if not output["results"]:
        print("\nNo chunks found. Build the ChromaDB vector store first:")
        print('python backend/benchmark_vector_store.py "https://stthomascollege.ac.in/" --query "What courses are offered?"')
        return

    print("\nTop chunks:")
    for index, result in enumerate(output["results"], start=1):
        print(f"\n{index}. {result.get('title', 'Untitled')} | score={result.get('score', 0):.4f}")
        print(result.get("url", ""))
        print(result.get("text", "")[:500])


if __name__ == "__main__":
    main()

