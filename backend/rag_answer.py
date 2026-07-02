import argparse
import json
from pathlib import Path

from langchain_rag import LangChainRAGPipeline
from retriever import DEFAULT_CHROMA_DIR


def build_parser():
    parser = argparse.ArgumentParser(
        description="Ask a question using the LangChain RAG pipeline."
    )
    parser.add_argument("question", help="Question to answer.")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--persist-dir",
        default=str(DEFAULT_CHROMA_DIR),
        help="ChromaDB persistence directory.",
    )
    parser.add_argument("--json", action="store_true")
    return parser


def main():
    args = build_parser().parse_args()

    pipeline = LangChainRAGPipeline(
        persist_dir=Path(args.persist_dir),
        top_k=args.top_k,
    )
    output = pipeline.ask(args.question)

    if args.json:
        print(json.dumps(output, indent=2))
        return

    print("\n========== MODULE 8 LANGCHAIN RAG ==========")
    print(f"Question    : {output['question']}")
    print(f"Top K       : {output['top_k']}")
    print(f"LLM enabled : {output['used_llm']}")
    print("\nAnswer:\n")
    print(output["answer"])

    print("\nSources:")
    for index, source in enumerate(output["sources"], start=1):
        score = source.get("score")
        score_text = f"{score:.4f}" if isinstance(score, float) else "n/a"
        print(f"{index}. {source.get('title', 'Untitled')} | score={score_text}")
        print(source.get("url", ""))


if __name__ == "__main__":
    main()

