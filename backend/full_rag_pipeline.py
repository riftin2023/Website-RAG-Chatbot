import argparse
import json
import time
from pathlib import Path

from chunking import TextChunker
from embedding_config import EMBEDDING_MODEL, MODEL_LABEL
from embeddings import EmbeddingGenerator
from groq_generator import GroqAnswerGenerator
from pipeline import RAGPipeline
from vector_config import VECTOR_DB, VECTOR_DB_LABEL
from vector_store_factory import create_vector_store


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "vector_db"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run the complete RAG pipeline from website URL to final answer."
    )
    parser.add_argument("url", help="Website URL to ingest.")
    parser.add_argument("question", help="Question to answer.")
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--chunk-overlap", type=int, default=80)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Folder where full pipeline artifacts are saved.",
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


class FullRAGPipeline:
    def __init__(
        self,
        max_depth=1,
        chunk_size=500,
        chunk_overlap=80,
        top_k=5,
        output_dir=DEFAULT_OUTPUT_DIR,
    ):
        self.max_depth = max_depth
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.output_dir = Path(output_dir).resolve()

    def run(self, url, question):
        started_at = time.perf_counter()

        ingestion_pipeline = RAGPipeline(max_depth=self.max_depth)
        documents = ingestion_pipeline.ingest_website(url)

        chunker = TextChunker(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        chunks = chunker.chunk_documents(documents)

        if not chunks:
            raise RuntimeError("No chunks were generated. Check the URL or scraper output.")

        embedding_generator = EmbeddingGenerator(EMBEDDING_MODEL)
        texts = [chunk["text"] for chunk in chunks]
        embeddings, embedding_seconds = embedding_generator.encode(texts)
        query_embeddings, query_embedding_seconds = embedding_generator.encode([question])

        vector_output_dir = self.output_dir / VECTOR_DB
        vector_output_dir.mkdir(parents=True, exist_ok=True)

        vector_store = create_vector_store(
            embedding_dimension=int(embeddings.shape[1]),
            output_dir=vector_output_dir,
            reset=True,
        )
        vector_store.add(embeddings, chunks)
        vector_store.save(vector_output_dir)

        retrieved_chunks = vector_store.search(query_embeddings[0], top_k=self.top_k)
        context = format_context(retrieved_chunks)

        answer_generator = GroqAnswerGenerator()
        generation = answer_generator.generate(question, context)

        total_seconds = time.perf_counter() - started_at

        result = {
            "url": url,
            "question": question,
            "answer": generation["answer"],
            "used_llm": generation["used_llm"],
            "llm_model": generation["model"],
            "llm_temperature": generation["temperature"],
            "embedding_model": EMBEDDING_MODEL,
            "embedding_model_label": MODEL_LABEL,
            "vector_db": VECTOR_DB,
            "vector_db_label": VECTOR_DB_LABEL,
            "document_count": len(documents),
            "chunk_count": len(chunks),
            "top_k": self.top_k,
            "retrieved_chunks": retrieved_chunks,
            "embedding_seconds": embedding_seconds,
            "query_embedding_seconds": query_embedding_seconds,
            "total_seconds": total_seconds,
        }

        self.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.output_dir / "full_rag_result.json"
        report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        result["report_path"] = str(report_path)

        return result


def main():
    args = build_parser().parse_args()

    pipeline = FullRAGPipeline(
        max_depth=args.max_depth,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        top_k=args.top_k,
        output_dir=args.output_dir,
    )
    result = pipeline.run(args.url, args.question)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("\n========== MODULE 10 FULL RAG PIPELINE ==========")
    print(f"URL         : {result['url']}")
    print(f"Question    : {result['question']}")
    print(f"Embedding   : {result['embedding_model_label']}")
    print(f"Vector DB   : {result['vector_db_label']}")
    print(f"LLM model   : {result['llm_model']}")
    print(f"LLM enabled : {result['used_llm']}")
    print(f"Documents   : {result['document_count']}")
    print(f"Chunks      : {result['chunk_count']}")
    print(f"Total time  : {result['total_seconds']:.2f}s")
    print(f"Report      : {result['report_path']}")

    print("\nAnswer:\n")
    print(result["answer"])

    print("\nTop chunks:")
    for index, chunk in enumerate(result["retrieved_chunks"], start=1):
        score = chunk.get("score")
        score_text = f"{score:.4f}" if isinstance(score, float) else "n/a"
        print(f"\n{index}. {chunk.get('title', 'Untitled')} | score={score_text}")
        print(chunk.get("url", ""))
        print(chunk.get("text", "")[:300])


if __name__ == "__main__":
    main()


