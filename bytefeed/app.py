import asyncio
import html
import re
import webbrowser
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, ListItem, ListView, Static, Markdown, Input, TabbedContent, TabPane
from textual.binding import Binding
from textual import work

from bytefeed.config import load_or_create_config, CONFIG_FILE
from bytefeed.RSS import RSSWorker, FeedArticle


def slugify(text: str) -> str:
    """Sanitizes category titles into valid Textual CSS identifiers."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text.lower())


class NewsItem(ListItem):
    """Custom List Item storing feed article metadata."""

    def __init__(self, article: FeedArticle):
        super().__init__()
        self.article = article

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold cyan][{self.article.source}][/bold cyan] {self.article.title}\n"
            f"[dim]{self.article.published}[/dim]"
        )


class ByteFeedApp(App):
    """Modern 2026 Reactive Terminal UI News Aggregator."""

    TITLE = "ByteFeed TUI"
    SUB_TITLE = "Real-Time Terminal News Feed"

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
        Binding("o", "open_in_browser", "Open in Browser", show=True),
        Binding("/", "focus_search", "Search", show=True),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.config = load_or_create_config()
        self.rss_worker = RSSWorker()
        self.selected_article: FeedArticle | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Initializing ByteFeed engine...", id="status-bar")

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Input(placeholder="🔍 Filter headlines...", id="search-box")
                with TabbedContent(id="category-tabs"):
                    for cat in self.config.get("categories", {}).keys():
                        clean_id = slugify(cat)
                        with TabPane(cat, id=f"tab-{clean_id}"):
                            # Just yield the ListView without adding items
                            yield ListView(id=f"list-{clean_id}")

            with VerticalScroll(id="main-content"):
                yield Markdown(
                    "# Welcome to ByteFeed ⚡\n\n"
                    "Select any article from the left pane to view details.\n\n"
                    "- Press `/` to search headlines\n"
                    "- Press `o` to open selected article in browser\n"
                    "- Press `r` to manually refresh feeds\n"
                    "- Press `q` to exit",
                    id="article-view",
                )

        yield Footer()

    def on_mount(self) -> None:
        """App initialization."""
        interval = self.config.get("refresh_interval_seconds", 60)
        self.set_interval(interval, self.trigger_refresh)
        # Start the initial fetch
        self.run_worker(self.fetch_all_feeds())

    def trigger_refresh(self) -> None:
        """Trigger a refresh of all feeds."""
        self.run_worker(self.fetch_all_feeds())

    async def fetch_all_feeds(self) -> None:
        """Fetch all feeds and update the UI."""
        status = self.query_one("#status-bar", Static)
        status.update("🔄 Syncing RSS streams...")

        categories = self.config.get("categories", {})
        
        if not categories:
            status.update("⚠️ No categories configured")
            return
        
        # Process each category
        for cat_name, feeds in categories.items():
            clean_id = slugify(cat_name)
            
            try:
                # Fetch all feeds concurrently inside the category
                tasks = [
                    self.rss_worker.fetch_feed(source_name=feed["name"], url=feed["url"])
                    for feed in feeds
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                articles = []
                for res in results:
                    if isinstance(res, list):
                        articles.extend(res)
                    elif isinstance(res, Exception):
                        print(f"Error fetching feed: {res}")

                # Update the list view
                try:
                    list_view = self.query_one(f"#list-{clean_id}", ListView)
                except Exception as e:
                    print(f"Could not find list view for {clean_id}: {e}")
                    continue
                
                # Clear existing items
                list_view.clear()
                
                # Add new items
                if articles:
                    for article in articles:
                        list_view.append(NewsItem(article))
                    print(f"✅ Loaded {len(articles)} articles for {cat_name}")
                else:
                    # Add a placeholder if no articles
                    list_view.append(
                        ListItem(Static("[dim]No articles found[/dim]"))
                    )
                    print(f"⚠️ No articles found for {cat_name}")

                # Force a refresh of the widget
                list_view.refresh()

            except Exception as err:
                print(f"❌ Error fetching {cat_name}: {err}")
                status.update(f"⚠️ Error fetching {cat_name}: {str(err)[:30]}")
                # Add error message to the list
                try:
                    list_view = self.query_one(f"#list-{clean_id}", ListView)
                    list_view.clear()
                    list_view.append(
                        ListItem(Static(f"[red]Error loading feeds[/red]"))
                    )
                    list_view.refresh()
                except:
                    pass

        # Update status bar
        status.update(
            f"✅ ByteFeed Active | Auto-sync every {self.config.get('refresh_interval_seconds', 60)}s"
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection of a news item."""
        if isinstance(event.item, NewsItem):
            self.selected_article = event.item.article
            doc = (
                f"# {self.selected_article.title}\n\n"
                f"**Source:** {self.selected_article.source}  \n"
                f"**Published:** {self.selected_article.published}  \n"
                f"**URL:** [{self.selected_article.link}]({self.selected_article.link})\n\n"
                f"---\n\n"
                f"{self.selected_article.summary}"
            )
            self.query_one("#article-view", Markdown).update(doc)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter articles based on search query."""
        query = event.value.lower().strip()
        try:
            list_view = self.query_one(ListView)
            for child in list_view.children:
                if isinstance(child, NewsItem):
                    if not query:
                        child.display = True
                    else:
                        child.display = (
                            query in child.article.title.lower()
                            or query in child.article.source.lower()
                        )
                else:
                    child.display = True
        except Exception:
            pass

    def action_focus_search(self) -> None:
        """Focus the search box."""
        self.query_one("#search-box", Input).focus()

    def action_refresh_feed(self) -> None:
        """Manually refresh the feeds."""
        self.trigger_refresh()

    def action_open_in_browser(self) -> None:
        """Open the selected article in a browser."""
        if self.selected_article and self.selected_article.link:
            webbrowser.open(self.selected_article.link)
            status = self.query_one("#status-bar", Static)
            status.update(f"🌐 Opened: {self.selected_article.title[:50]}...")


def main():
    app = ByteFeedApp()
    app.run()


if __name__ == "__main__":
    main()