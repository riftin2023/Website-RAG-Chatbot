import re

from bs4 import BeautifulSoup


class TextPreprocessor:
    def remove_html(self, text):
        soup = BeautifulSoup(text or "", "html.parser")
        return soup.get_text(separator=" ")

    def remove_urls(self, text):
        return re.sub(r"https?://\S+|www\.\S+", "", text)

    def remove_emails(self, text):
        return re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            "",
            text,
        )

    def remove_extra_whitespace(self, text):
        return re.sub(r"\s+", " ", text).strip()

    def remove_special_characters(self, text):
        return re.sub(r"[^A-Za-z0-9.,!?():;/%\- ]", "", text)

    def preprocess(self, text):
        text = self.remove_html(text)
        text = self.remove_urls(text)
        text = self.remove_emails(text)
        text = self.remove_special_characters(text)
        text = self.remove_extra_whitespace(text)
        return text

