import requests
from bs4 import BeautifulSoup
from readability import Document

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 TextGateway/1.0"
)
TIMEOUT = 15
MAX_BYTES = 5 * 1024 * 1024


class ExtractEngine:
    def __init__(self, timeout: int = TIMEOUT, max_bytes: int = MAX_BYTES) -> None:
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def extract(self, url: str) -> dict:
        resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
        resp.raise_for_status()
        if len(resp.content) > self.max_bytes:
            raise ValueError("页面内容超过大小限制（5MB）")
        resp.encoding = resp.apparent_encoding or resp.encoding
        html = resp.text
        doc = Document(html)
        title = doc.short_title()
        summary = doc.summary()
        soup = BeautifulSoup(summary, "lxml")
        text = soup.get_text(separator="\n", strip=True)
        return {"url": url, "title": title, "text": text}
