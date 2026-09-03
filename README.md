# ByteFeed ⚡

> A modern, asynchronous Terminal UI (TUI) news aggregator engineered for Windows Terminal and modern CLI environments.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- ⚡ **Asynchronous RSS Engine:** Non-blocking background fetches powered by `httpx` and `feedparser`.
- 🎨 **Modern Split-Pane TUI:** Built with `Textual` using smooth layout grids and custom CSS styles.
- 📁 **Dynamic Config Support:** Fully configurable via `~/.config/bytefeed/config.json`.
- 🔍 **Live Filtering & Browser Launch:** Instant headline search filtering and direct link opening in your default browser.

## Quick Installation

Clone the repository and install locally in editable mode:

```bash
git clone [https://github.com/yourusername/bytefeed.git](https://github.com/yourusername/bytefeed.git)
cd bytefeed
pip install -e .
```

Now you can launch ByteFeed anywhere in your terminal:

```bash
bytefeed
# or simply
bf
```

Here is the complete implementation for the remaining files in the `bytefeed` repository, wired up cleanly for production and GitHub ready.

---

### 1. `newsfeed/__init__.py`

```python
"""ByteFeed - Modern 2026 Async Terminal UI News Engine."""

__version__ = "0.1.0"

```

---

### 2. `newsfeed/app.py`

This is the main Textual application logic that pulls together `config.py` and `RSS.py`.

```python
import webbrowser
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, ListItem, ListView, Static, Markdown, Input, TabbedContent, TabPane
from textual.binding import Binding

from newsfeed.config import load_or_create_config, CONFIG_FILE
from newsfeed.RSS import RSSWorker, FeedArticle


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
                        with TabPane(cat, id=f"tab-{cat}"):
                            yield ListView(id=f"list-{cat}")

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

    async def on_mount(self) -> None:
        interval = self.config.get("refresh_interval_seconds", 60)
        self.set_interval(interval, self.fetch_all_feeds)
        await self.fetch_all_feeds()

    async def fetch_all_feeds(self) -> None:
        status = self.query_one("#status-bar", Static)
        status.update("Syncing RSS streams...")

        categories = self.config.get("categories", {})
        for cat_name, feeds in categories.items():
            articles = []
            for feed in feeds:
                fetched = await self.rss_worker.fetch_feed(
                    source_name=feed["name"], url=feed["url"]
                )
                articles.extend(fetched)

            try:
                list_view = self.query_one(f"#list-{cat_name}", ListView)
                await list_view.clear()
                for article in articles:
                    await list_view.append(NewsItem(article))
            except Exception:
                pass

        status.update(
            f"ByteFeed Active | Auto-sync every {self.config.get('refresh_interval_seconds', 60)}s | Config: {CONFIG_FILE}"
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
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
        query = event.value.lower()
        try:
            active_list = self.query_one(ListView)
            for child in active_list.children:
                if isinstance(child, NewsItem):
                    child.display = (
                        query in child.article.title.lower()
                        or query in child.article.source.lower()
                    )
        except Exception:
            pass

    def action_focus_search(self) -> None:
        self.query_one("#search-box", Input).focus()

    async def action_refresh_feed(self) -> None:
        await self.fetch_all_feeds()

    def action_open_in_browser(self) -> None:
        if self.selected_article and self.selected_article.link:
            webbrowser.open(self.selected_article.link)


def main():
    app = ByteFeedApp()
    app.run()


if __name__ == "__main__":
    main()

```

---

### 3. `tests/test_parser.py`

Basic test suite for verifying config generation and RSS parsing logic via `pytest`.

```python
import pytest
from newsfeed.config import load_or_create_config
from newsfeed.RSS import RSSWorker

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

```

---

### 4. `pyproject.toml`

Modern build metadata file configuring dependencies, CLI entrypoint, and test tools.

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "bytefeed"
version = "0.1.0"
description = "A modern, asynchronous 2026 Terminal UI News Feed for Windows Terminal."
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Tuncay"}
]
dependencies = [
    "textual>=0.50.0",
    "feedparser>=6.0.10",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0"
]

[project.scripts]
bytefeed = "newsfeed.app:main"
bf = "newsfeed.app:main"

[tool.pytest.ini_options]
asyncio_mode = "auto"

```

---

### 5. `requirements.txt`

```text
textual>=0.50.0
feedparser>=6.0.10
httpx>=0.27.0
pytest>=8.0.0
pytest-asyncio>=0.23.0

```

---

### 6. `.github/workflows/python-app.yml`

GitHub Action workflow for automatic syntax checking and test execution on push/PR.

```yaml
name: ByteFeed CI

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install .[dev]
      - name: Run Pytest
        run: |
          pytest
```

---

### 7. `.gitignore`

```text
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environments
.venv
venv/
ENV/

# Pytest / Coverage
.pytest_cache/
.coverage
htmlcov/

# IDE / OS
.vscode/
.idea/
.DS_Store
Thumbs.db

```

---

### 8. `README.md`

````markdown
# ByteFeed ⚡

> A modern, asynchronous Terminal UI (TUI) news aggregator engineered for Windows Terminal and modern CLI environments.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- ⚡ **Asynchronous RSS Engine:** Non-blocking background fetches powered by `httpx` and `feedparser`.
- 🎨 **Modern Split-Pane TUI:** Built with `Textual` using smooth layout grids and custom CSS styles.
- 📁 **Dynamic Config Support:** Fully configurable via `~/.config/bytefeed/config.json`.
- 🔍 **Live Filtering & Browser Launch:** Instant headline search filtering and direct link opening in your default browser.

## Quick Installation

Clone the repository and install locally in editable mode:

```bash
git clone [https://github.com/yourusername/bytefeed.git](https://github.com/yourusername/bytefeed.git)
cd bytefeed
pip install -e .
```
````

Now you can launch ByteFeed anywhere in your terminal:

```bash
bytefeed
# or simply
bf

```

## Keybindings

| Key | Action                                   |
| --- | ---------------------------------------- |
| `/` | Focus search filter                      |
| `o` | Open selected article in default browser |
| `r` | Force refresh all feeds                  |
| `q` | Quit application                         |

### 9. `LICENSE`

```text
MIT License

Copyright (c) 2026 Tuncay

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
