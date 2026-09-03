import json
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".config" / "bytefeed"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "refresh_interval_seconds": 60,
    "categories": {
        "Tech": [
            {"name": "Hacker News", "url": "https://news.ycombinator.com/rss"},
            {"name": "Ars Technica", "url": "http://feeds.arstechnica.com/arstechnica/index"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"}
        ],
        "AI & Dev": [
            {"name": "Lobsters", "url": "https://lobste.rs/rss"},
            {"name": "GitHub Blog", "url": "https://github.blog/feed/"},
            {"name": "DEV Community", "url": "https://dev.to/feed"}
        ],
        "Security": [
            {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
            {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
            {"name": "Krebs on Security", "url": "https://krebsonsecurity.com/feed/"}
        ]
    }
}

def load_or_create_config() -> Dict[str, Any]:
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG