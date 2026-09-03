import asyncio
from bytefeed.RSS import RSSWorker
from bytefeed.config import load_or_create_config

async def test_feeds():
    worker = RSSWorker()
    config = load_or_create_config()
    
    for cat_name, feeds in config.get("categories", {}).items():
        print(f"\n📡 Testing {cat_name}...")
        for feed in feeds:
            print(f"  Fetching {feed['name']} from {feed['url']}")
            articles = await worker.fetch_feed(feed["name"], feed["url"], limit=3)
            print(f"    Got {len(articles)} articles")
            if articles:
                print(f"    First: {articles[0].title[:50]}...")
            print()

if __name__ == "__main__":
    asyncio.run(test_feeds())