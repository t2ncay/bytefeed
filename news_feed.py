import asyncio
import json
import html
import webbrower
from pathlib import Path
from datetime import datetime
import feedparser
import httpx

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from textual.widgets import Header, Footer, ListItem, ListView, Static, Markdown, Input, TabbedContent, TabPane
from textual.binding import Binding

# Config path resolution
CONFIG_DIR = Path.home() / ".config" / "terminal-news"
CONFIG_FILE = CONFIG_DIR / "feeds.json"

DEFAULT_CONFIG = {
    "refresh_interval_seconds": 60,
    "categories": {
        "Tech": [
            {"name": "Hacker News", "url": "https://news.ycombinator.com/rss"},
            {"name": "Ars Technica", "url": "http://feeds.arstechnica.com/arstechnica/index"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"}
        ],
        "AI & Dev": [
            {"name": "Lobsters", "url": "https://lobste.rs/rss"},
            {"name": "GitHub Blog", "url": "https://github.blog/feed/"}
        ],
        "Security": [
            {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
            {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"}
        ]
    }
}


def load_or_create_config():
    """Loads configuration file or writes defaults if missing."""
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


class NewsItem(ListItem):
    """Custom List Item holding metadata for rendering and actions."""
    def __init__(self, title: str, summary: str, link: str, published: str, source: str):
        super().__init__()
        self.item_title = title
        self.summary = summary
        self.link = link
        self.published = published
        self.source = source

    def compose(self) -> ComposeResult:
        yield Static(f"[bold cyan][{self.source}][/bold cyan] {self.item_title}\n[dim]{self.published}[/dim]")


class AdvancedNewsFeed(App):
    """Modern 2026 Reactive Terminal UI News Engine."""

    TITLE = "Terminal News Feed Engine"
    SUB_TITLE = "Live Async Feed Aggregator"

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 1fr 2fr;
        background: $surface;
    }

    #sidebar {
        border-right: heavy $primary;
        height: 100%;
        padding: 0 1;
    }

    #main-content {
        height: 100%;
        padding: 1 2;
    }

    #search-box {
        margin-bottom: 1;
        border: round $secondary;
    }

    #status-bar {
        dock: top;
        height: 1;
        background: $accent;
        color: $text;
        text-style: bold;
        padding: 0 1;
    }

    ListView {
        height: 100%;
        border: round $primary;
        background: $surface-darken-1;
    }

    ListItem {
        padding: 1;
        border-bottom: solid $surface-lighten-1;
    }

    ListItem:hover {
        background: $accent-darken-2;
    }

    #article-view {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh_feed", "Sync Feeds", show=True),
        Binding("o", "open_in_browser", "Open Link", show=True),
        Binding("/", "focus_search", "Search", show=True),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.config = load_or_create_config()
        self.all_items = []
        self.current_selected_item = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Initializing dynamic RSS engine...", id="status-bar")

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Input(placeholder="🔍 Search headlines...", id="search-box")
                with TabbedContent(id="category-tabs"):
                    for cat in self.config.get("categories", {}).keys():
                        with TabPane(cat, id=f"tab-{cat}"):
                            yield ListView(id=f"list-{cat}")

            with VerticalScroll(id="main-content"):
                yield Markdown("# Terminal News Aggregator v1.0\n\nSelect any feed item from the left panel to display contents.", id="article-view")

        yield Footer()

    async def on_mount(self) -> None:
        """App initialization and periodic sync schedule setup."""
        interval = self.config.get("refresh_interval_seconds", 60)
        self.set_interval(interval, self.fetch_all_feeds)
        await self.fetch_all_feeds()

    async def fetch_all_feeds(self) -> None:
        """Asynchronously fetch, parse, and update list views per category."""
        status = self.query_one("#status-bar", Static)
        status.update(f"Syncing RSS endpoints... [{datetime.now().strftime('%H:%M:%S')}]")

        categories = self.config.get("categories", {})
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for cat_name, feeds in categories.items():
                items = []
                for feed in feeds:
                    try:
                        res = await client.get(feed["url"])
                        parsed = feedparser.parse(res.text)
                        for entry in parsed.entries[:7]:
                            published = entry.get("published", entry.get("updated", "Recently"))
                            summary = entry.get("summary", entry.get("description", "No content preview available."))
                            items.append(NewsItem(
                                title=entry.title,
                                summary=html.unescape(summary),
                                link=entry.link,
                                published=published,
                                source=feed["name"]
                            ))
                    except Exception:
                        continue

                # Populate corresponding list view
                try:
                    list_view = self.query_one(f"#list-{cat_name}", ListView)
                    await list_view.clear()
                    for item in items:
                        await list_view.append(item)
                except Exception:
                    pass

        status.update(f"Active | Auto-sync every {self.config.get('refresh_interval_seconds', 60)}s | Config: {CONFIG_FILE}")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handler for selecting news items."""
        if isinstance(event.item, NewsItem):
            self.current_selected_item = event.item
            doc = (
                f"# {event.item.item_title}\n\n"
                f"**Source:** {event.item.source}  \n"
                f"**Published:** {event.item.published}  \n"
                f"**URL:** [{event.item.link}]({event.item.link})\n\n"
                f"---\n\n"
                f"{event.item.summary}"
            )
            self.query_one("#article-view", Markdown).update(doc)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Client-side live title filtering."""
        query = event.value.lower()
        # Filter visible items in currently active list view dynamically
        try:
            active_list = self.query_one(ListView)
            for child in active_list.children:
                if isinstance(child, NewsItem):
                    child.display = query in child.item_title.lower() or query in child.source.lower()
        except Exception:
            pass

    def action_focus_search(self) -> None:
        """Shortcut action for '/'."""
        self.query_one("#search-box", Input).focus()

    async def action_refresh_feed(self) -> None:
        """Shortcut action for 'r'."""
        await self.fetch_all_feeds()

    def action_open_in_browser(self) -> None:
        """Opens selected article URL in default system browser."""
        if self.current_selected_item and self.current_selected_item.link:
            import webbrowser
            webbrowser.open(self.current_selected_item.link)


if __name__ == "__main__":
    app = AdvancedNewsFeed()
    app.run()