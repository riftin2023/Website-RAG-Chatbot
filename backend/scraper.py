# backend/scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class WebsiteScraper:
    def __init__(self, max_depth=2):
        self.max_depth = max_depth
        self.visited = set()

        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and parsed.netloc != ""

    def clean_text(self, soup):
        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "noscript"
        ]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)

    def extract_internal_links(self, soup, base_url):
        links = []

        base_domain = urlparse(base_url).netloc

        for anchor in soup.find_all("a", href=True):

            absolute_url = urljoin(base_url, anchor["href"])

            parsed = urlparse(absolute_url)

            # Ignore external websites
            if parsed.netloc != base_domain:
                continue

            # Remove fragments
            absolute_url = absolute_url.split("#")[0]

            if absolute_url not in links:
                links.append(absolute_url)

        return links

    def scrape_page(self, url):

        response = self.session.get(
            url,
            headers=self.headers,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title else "Untitled"

        text = self.clean_text(soup)

        links = self.extract_internal_links(soup, url)

        return {
            "url": url,
            "title": title,
            "text": text,
            "links": links
        }

    def crawl(self, url, depth=0):

        if depth > self.max_depth:
            return []

        if url in self.visited:
            return []

        if not self.is_valid_url(url):
            return []

        self.visited.add(url)

        try:

            print(f"Crawling: {url}")

            page = self.scrape_page(url)

            documents = [page]

            for link in page["links"]:
                documents.extend(
                    self.crawl(link, depth + 1)
                )

            return documents

        except Exception as e:

            print(f"Failed: {url}")

            print(e)

            return []


if __name__ == "__main__":

    scraper = WebsiteScraper(max_depth=1)

    website = "https://stthomascollege.ac.in/"

    documents = scraper.crawl(website)

    print("\nTotal Pages Crawled:", len(documents))

    print("\nFirst Page")

    print("=" * 50)

    print("Title:", documents[0]["title"])

    print("\nURL:", documents[0]["url"])

    print("\nText Preview:\n")

    print(documents[0]["text"][:1000])