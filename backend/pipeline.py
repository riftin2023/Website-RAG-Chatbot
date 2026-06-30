from scraper import WebsiteScraper
from preprocessing import TextPreprocessor


class RAGPipeline:
    def __init__(self, max_depth=1):
        self.scraper = WebsiteScraper(max_depth=max_depth)
        self.preprocessor = TextPreprocessor()

    def normalize_url(self, url):
        url = url.strip()

        if not url:
            raise ValueError("Website URL cannot be empty.")

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return url

    def ingest_website(self, url):
        url = self.normalize_url(url)

        print("\n========== STEP 1 ==========")
        print(f"Scraping website: {url}\n")

        documents = self.scraper.crawl(url)
        print(f"\nPages scraped: {len(documents)}")

        if not documents:
            print("No pages found.")
            return []

        print("\n========== STEP 2 ==========")
        print("Preprocessing text...\n")

        cleaned_documents = []

        for document in documents:
            cleaned_text = self.preprocessor.preprocess(document.get("text", ""))

            cleaned_documents.append(
                {
                    "url": document.get("url", ""),
                    "title": document.get("title", "Untitled"),
                    "text": cleaned_text,
                    "links": document.get("links", []),
                }
            )

        print(f"Preprocessed {len(cleaned_documents)} documents.")
        return cleaned_documents


if __name__ == "__main__":
    pipeline = RAGPipeline(max_depth=1)

    website = input("Enter Website URL: ")
    documents = pipeline.ingest_website(website)

    print("\n========== RESULT ==========\n")

    if not documents:
        print("No documents to display.")
    else:
        for index, document in enumerate(documents, start=1):
            print(f"Document {index}")
            print("Title :", document["title"])
            print("URL   :", document["url"])
            print("\nPreview:\n")
            print(document["text"][:500])
            print("\n" + "=" * 80 + "\n")