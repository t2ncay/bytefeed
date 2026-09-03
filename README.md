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
