import json
from pathlib import Path

import faiss  # type: ignore[import]
import numpy as np


class FaissVectorStore:
    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunks = []

    def add(self, embeddings, chunks):
        vectors = np.asarray(embeddings, dtype="float32")

        if vectors.ndim != 2:
            raise ValueError("embeddings must be a 2D array.")

        if vectors.shape[1] != self.dimension:
            raise ValueError("embedding dimension does not match FAISS index dimension.")

        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(self, query_embedding, top_k=5):
        query = np.asarray([query_embedding], dtype="float32")
        scores, indexes = self.index.search(query, top_k)

        results = []

        for score, index in zip(scores[0], indexes[0]):
            if index == -1:
                continue

            chunk = dict(self.chunks[int(index)])
            chunk["score"] = float(score)
            results.append(chunk)

        return results

    def save(self, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(output_dir / "faiss.index"))
        (output_dir / "faiss_chunks.json").write_text(
            json.dumps(self.chunks, indent=2),
            encoding="utf-8",
        )

