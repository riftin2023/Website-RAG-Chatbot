import time

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts):
        started_at = time.perf_counter()
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        elapsed_seconds = time.perf_counter() - started_at

        return embeddings.astype("float32"), elapsed_seconds


def cosine_similarity(query_embedding, document_embeddings):
    query = np.asarray(query_embedding, dtype="float32")
    documents = np.asarray(document_embeddings, dtype="float32")

    return np.dot(documents, query)


def top_k_similar(query_embedding, document_embeddings, chunks, k=5):
    scores = cosine_similarity(query_embedding, document_embeddings)
    ranked_indexes = np.argsort(scores)[::-1][:k]

    results = []

    for index in ranked_indexes:
        result = dict(chunks[int(index)])
        result["score"] = float(scores[int(index)])
        results.append(result)

    return results

