import argparse
import json
from pathlib import Path

from openai_generator import OpenAIAnswerGenerator
from retriever import DEFAULT_CHROMA_DIR, Retriever


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate a grounded answer with OpenAI using retrieved website context."
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


def format_context(chunks):
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


def main():
    args = build_parser().parse_args()

    retriever = Retriever(
        persist_dir=Path(args.persist_dir),
        top_k=args.top_k,
    )
    retrieval = retriever.retrieve(args.question)
    context = format_context(retrieval["results"])

    generator = OpenAIAnswerGenerator()
    generation = generator.generate(args.question, context)

    output = {
        "question": args.question,
        "answer": generation["answer"],
        "used_llm": generation["used_llm"],
        "model": generation["model"],
        "temperature": generation["temperature"],
        "top_k": retrieval["top_k"],
        "sources": retrieval["results"],
    }

    if args.json:
        print(json.dumps(output, indent=2))
        return

    print("\n========== MODULE 9 OPENAI ANSWER ==========")
    print(f"Question    : {output['question']}")
    print(f"Model       : {output['model']}")
    print(f"Temperature : {output['temperature']}")
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

