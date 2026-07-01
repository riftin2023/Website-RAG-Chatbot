from pathlib import Path

import chromadb  # type: ignore[import]


class ChromaVectorStore:
    def __init__(self, persist_dir, collection_name="website_chunks"):
        persist_dir = Path(persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(collection_name)

    def add(self, embeddings, chunks):
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "url": chunk.get("url", ""),
                "title": chunk.get("title", "Untitled"),
                "chunk_index": chunk.get("chunk_index", 0),
            }
            for chunk in chunks
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
        )

    def search(self, query_embedding, top_k=5):
        response = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
        )

        results = []

        ids = response.get("ids", [[]])[0]
        documents = response.get("documents", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]

        for item_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
            result = dict(metadata or {})
            result["id"] = item_id
            result["text"] = text
            result["distance"] = float(distance)
            result["score"] = 1.0 - float(distance)
            results.append(result)

        return results

    def save(self, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

