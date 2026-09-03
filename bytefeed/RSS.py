# bytefeed/RSS.py
import html
from dataclasses import dataclass
from typing import List
import feedparser
import httpx


@dataclass
class FeedArticle:
    title: str
    summary: str
    link: str
    published: str
    source: str


class RSSWorker:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ByteFeed/1.0"
        }
        self._client: httpx.AsyncClient | None = None

    async def get_client(self) -> httpx.AsyncClient:
        """Reuse a single AsyncClient instance to avoid connection pool deadlocks."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=self.headers,
                verify=True
            )
        return self._client

    async def fetch_feed(self, source_name: str, url: str, limit: int = 7) -> List[FeedArticle]:
        articles: List[FeedArticle] = []
        try:
            client = await self.get_client()
            response = await client.get(url)
            if response.status_code == 200:
                parsed = feedparser.parse(response.text)
                for entry in parsed.entries[:limit]:
                    published = entry.get("published", entry.get("updated", "Recently"))
                    summary = entry.get("summary", entry.get("description", "No content preview available."))
                    
                    articles.append(
                        FeedArticle(
                            title=entry.title,
                            summary=html.unescape(summary),
                            link=entry.link,
                            published=published,
                            source=source_name
                        )
                    )
        except Exception as e:
            print(f"[Error fetching {source_name} ({url})]: {e}")

        return articles

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()