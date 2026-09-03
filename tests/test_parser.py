import pytest
from bytefeed.config import load_or_create_config
from bytefeed.RSS import RSSWorker

def test_config_loader():
    config = load_or_create_config()
    assert "categories" in config
    assert "refresh_interval_seconds" in config

@pytest.mark.asyncio
async def test_rss_fetcher():
    worker = RSSWorker(timeout=5.0)
    # Test fetch against Hacker News feed
    articles = await worker.fetch_feed("HN", "https://news.ycombinator.com/rss", limit=2)
    assert isinstance(articles, list)
    if len(articles) > 0:
        assert articles[0].title != ""
        assert articles[0].link.startswith("http")