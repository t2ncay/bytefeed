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
git clone https://github.com/t2ncay/bytefeed.git
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

## Keybindings

| Key | Action                                   |
| --- | ---------------------------------------- |
| `/` | Focus search filter                      |
| `o` | Open selected article in default browser |
| `r` | Force refresh all feeds                  |
| `q` | Quit application                         |
