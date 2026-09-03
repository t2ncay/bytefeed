<div align="center">

# ByteFeed ⚡

**A terminal news aggregator that doesn't get in your way.**

Async RSS fetching, a split-pane TUI, live search — all from your keyboard, no browser tab required.

![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![Textual](https://img.shields.io/badge/built%20with-Textual-4B0082)
![License](https://img.shields.io/badge/license-MIT-2ea44f)
![Platform](https://img.shields.io/badge/platform-Windows%20Terminal-0078D6?logo=windowsterminal&logoColor=white)

</div>

---

## What it does

ByteFeed pulls from a set of RSS feeds in the background and lays them out in a split-pane terminal UI — categories on the left, article content on the right. No polling scripts, no fifteen browser tabs, no ads. Just headlines, updated on an interval you control.

- **Async fetching** — feeds within a category are pulled concurrently via `httpx`, so one slow source doesn't block the rest
- **Category tabs** — articles are grouped and browsable by tab, driven entirely by your config
- **Live search** — `/` filters the current list by title or source as you type
- **One-key browser handoff** — `o` opens the selected article's link in your default browser
- **Auto-refresh** — feeds resync on a configurable interval, or on demand with `r`

## Install

```bash
git clone https://github.com/t2ncay/bytefeed.git
cd bytefeed
pip install -e .
```

Run it from anywhere:

```bash
bytefeed
# or the short form
bf
```

## Keybindings

| Key       | Action                           |
| --------- | -------------------------------- |
| `/`       | Focus the search box             |
| `o`       | Open selected article in browser |
| `r`       | Force-refresh all feeds          |
| `j` / `k` | Move down / up in the list       |
| `q`       | Quit                             |

## Configuration

ByteFeed reads from `~/.config/bytefeed/config.json`, generated with sane defaults on first run. Edit it to add categories, swap feeds, or change the sync interval:

| Key                        | Type     | Description                                        |
| -------------------------- | -------- | -------------------------------------------------- |
| `refresh_interval_seconds` | `int`    | How often feeds auto-refresh, in seconds           |
| `categories`               | `object` | Category name → list of `{name, url}` feed sources |

Changes take effect the next time ByteFeed starts, or on a manual refresh once reloaded.

### Default sources

| Category | Source            | Feed                                                                                        |
| -------- | ----------------- | ------------------------------------------------------------------------------------------- |
| Tech     | Hacker News       | [`news.ycombinator.com/rss`](https://news.ycombinator.com/rss)                              |
| Tech     | Ars Technica      | [`feeds.arstechnica.com/arstechnica/index`](http://feeds.arstechnica.com/arstechnica/index) |
| Tech     | TechCrunch        | [`techcrunch.com/feed`](https://techcrunch.com/feed/)                                       |
| AI & Dev | Lobsters          | [`lobste.rs/rss`](https://lobste.rs/rss)                                                    |
| AI & Dev | GitHub Blog       | [`github.blog/feed`](https://github.blog/feed/)                                             |
| AI & Dev | DEV Community     | [`dev.to/feed`](https://dev.to/feed)                                                        |
| Security | BleepingComputer  | [`bleepingcomputer.com/feed`](https://www.bleepingcomputer.com/feed/)                       |
| Security | The Hacker News   | [`feeds.feedburner.com/TheHackersNews`](https://feeds.feedburner.com/TheHackersNews)        |
| Security | Krebs on Security | [`krebsonsecurity.com/feed`](https://krebsonsecurity.com/feed/)                             |

All feed content is © its respective publisher; ByteFeed only aggregates and links out.

## Project layout

```text
bytefeed/
├── app.py        Textual application — layout, widgets, keybindings
├── RSS.py        Async feed fetcher (httpx + feedparser)
├── config.py     Config loading, defaults, ~/.config path handling
└── __init__.py
tests/
├── test_parser.py   Unit tests for config + fetcher
└── test_feeds.py    Live smoke test against real feed URLs
```

## Testing

```bash
pip install -e ".[dev]"
pytest
```

`test_feeds.py` hits real feed URLs and prints what it gets back — useful for confirming a source is still alive after editing your config.

## License

MIT — see [`LICENSE.md`](LICENSE.md).
