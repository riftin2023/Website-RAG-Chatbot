class TextChunker:
    def __init__(self, chunk_size=500, chunk_overlap=80):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text):
        text = " ".join((text or "").split())

        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            start = end - self.chunk_overlap

        return chunks

    def chunk_documents(self, documents):
        chunked_documents = []

        for document_index, document in enumerate(documents):
            chunks = self.chunk_text(document.get("text", ""))

            for chunk_index, chunk in enumerate(chunks):
                chunked_documents.append(
                    {
                        "id": f"doc-{document_index}-chunk-{chunk_index}",
                        "url": document.get("url", ""),
                        "title": document.get("title", "Untitled"),
                        "text": chunk,
                        "chunk_index": chunk_index,
                    }
                )

        return chunked_documents

