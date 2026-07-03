import argparse
import json
from pathlib import Path

from answer_with_groq import format_context
from groq_generator import GroqAnswerGenerator
from retriever import DEFAULT_CHROMA_DIR, Retriever


DEFAULT_QUESTIONS = [
    "What is this website about?",
    "What contact information is available?",
    "What services, products, or programs are mentioned?",
]


def build_parser():
    parser = argparse.ArgumentParser(
        description="Test multiple arbitrary questions against the currently loaded ChromaDB website data."
    )
    parser.add_argument(
        "questions",
        nargs="*",
        help="Questions to test. If omitted, a small default set is used.",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--persist-dir",
        default=str(DEFAULT_CHROMA_DIR),
        help="ChromaDB persistence directory.",
    )
    parser.add_argument("--json", action="store_true")
    return parser


def answer_question(retriever, generator, question):
    retrieval = retriever.retrieve(question)
    context = format_context(retrieval["results"])
    generation = generator.generate(question, context)

    return {
        "question": question,
        "answer": generation["answer"],
        "used_llm": generation["used_llm"],
        "model": generation["model"],
        "top_k": retrieval["top_k"],
        "sources": retrieval["results"],
    }


def main():
    args = build_parser().parse_args()
    questions = args.questions or DEFAULT_QUESTIONS

    retriever = Retriever(
        persist_dir=Path(args.persist_dir),
        top_k=args.top_k,
    )
    generator = GroqAnswerGenerator()

    results = [
        answer_question(retriever, generator, question)
        for question in questions
    ]

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print("\n========== QUERY TEST ==========")
    print(f"Questions tested: {len(results)}")

    for index, result in enumerate(results, start=1):
        print(f"\n--- Query {index} ---")
        print(f"Question: {result['question']}")
        print(f"Model   : {result['model']}")
        print("\nAnswer:")
        print(result["answer"])

        print("\nSources:")
        for source_index, source in enumerate(result["sources"], start=1):
            score = source.get("score")
            score_text = f"{score:.4f}" if isinstance(score, float) else "n/a"
            print(
                f"{source_index}. {source.get('title', 'Untitled')} "
                f"| score={score_text} | {source.get('url', '')}"
            )


if __name__ == "__main__":
    main()
