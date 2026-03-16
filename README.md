# 🔍 Google MCP Server

**MCP server for Google services that have NO official API.**

YouTube Transcripts • Google Trends • News • Scholar • Books • Maps • Patents • NotebookLM — all in one MCP server.

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-brightgreen.svg)
![Tools](https://img.shields.io/badge/Tools-13-orange.svg)

---

## Why?

AI agents need Google data. Most Google services have **no official API** — try getting a YouTube transcript, Google Trends data, or Scholar citations programmatically. This MCP server wraps unofficial libraries and scraping into **13 clean MCP tools** that work with Claude Code, Cursor, Windsurf, or any MCP client.

**Zero cost for 10 of 13 tools.** No API keys needed.

---

## 🛠️ Tools

| Tool | What it does | Auth | Cost |
|------|-------------|------|------|
| `youtube_transcript` | Extract full transcript from any YouTube video | None | Free |
| `youtube_search` | Search YouTube videos by keyword | None | Free |
| `youtube_channel` | Get recent videos from a channel | None | Free |
| `google_trends` | Interest over time, trending topics | None | Free |
| `google_news` | Search news articles in real-time | None | Free |
| `google_scholar` | Search academic papers, citations | None* | Free |
| `books_search` | Search Google Books | None | Free |
| `maps_search` | Search Google Maps/Places | API Key | Free tier |
| `maps_details` | Place details, reviews, hours, phone | API Key | Free tier |
| `patents_search` | Search Google Patents | None | Free |
| `notebooklm_create` | Create NotebookLM notebook + add sources | Browser auth | Free |
| `notebooklm_podcast` | Generate audio podcast from notebook | Browser auth | Free |
| `research_pipeline` | **Combined multi-source research in one call** | None | Free |

*Google Scholar may rate-limit server IPs. Use a proxy for production.

---

## 🚀 Quick Start

```bash
git clone https://github.com/Miles0sage/google-mcp.git
cd google-mcp
pip install -r requirements.txt
```

### Add to Claude Code

Add to your `~/.mcp.json`:

```json
{
  "mcpServers": {
    "google-research": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/path/to/google-mcp"
    }
  }
}
```

### Docker

```bash
docker build -t google-mcp .
docker run -it google-mcp
```

---

## 💡 Examples

### Get a YouTube Transcript
```
Tool: youtube_transcript
Args: {"video_url": "https://youtube.com/watch?v=jGwO_UgTS7I"}

→ "Welcome to CS229 Machine Learning. Some of you know that this class
   has been taught at Stanford for a long time..." (69,877 chars)
```

### Search YouTube
```
Tool: youtube_search
Args: {"query": "AI agents tutorial 2026", "max_results": 3}

→ 1. How I'm Using AI Agents in 2026 — Tech With Tim (27K views)
  2. n8n Tutorial: How to Build AI Agents — Youri (57K views)
  3. Best AI Coding Tools for Developers 2026 — Mikey (13K views)
```

### Google Trends
```
Tool: google_trends
Args: {"keyword": "Claude AI", "timeframe": "today 1-m"}

→ Claude AI interest: 47 → 72 (53% increase over 30 days)
```

### Research Pipeline (multi-source)
```
Tool: research_pipeline
Args: {"topic": "autonomous AI agents architecture", "max_sources": 5}

→ NEWS: NVIDIA GTC 2026 agent infrastructure, Anthropic autonomy paper...
  ACADEMIC: [rate-limited on VPS, works locally]
  TRENDS: Interest spike Feb 2026
```

### Search Google Maps
```
Tool: maps_search
Args: {"query": "barbershops in Flagstaff AZ"}

→ 1. Surgeon Cuts — 4.9★ (127 reviews) — 123 N San Francisco St
  2. Floyd's 99 — 4.2★ (89 reviews) — 1800 S Milton Rd
  ...
```

---

## ⚙️ Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_MAPS_API_KEY` | For maps tools | Get free at [Google Cloud Console](https://console.cloud.google.com) ($200/mo free credit) |
| `PERPLEXITY_API_KEY` | Optional | Enhances research_pipeline with Perplexity Sonar |
| `NOTEBOOKLM_STORAGE_STATE` | For NotebookLM | Path to Playwright browser cookies (default: `~/.notebooklm/storage_state.json`) |

---

## 🏗️ Architecture

```
Claude Code / Cursor / Any MCP Client
        │
        ▼
   Google MCP Server (stdio)
        │
        ├── YouTube (youtube-transcript-api, scrapetube)
        ├── Google Trends (pytrends)
        ├── Google News (gnews)
        ├── Google Scholar (scholarly)
        ├── Google Books (free API)
        ├── Google Maps (googlemaps)
        ├── Google Patents (scraping)
        ├── NotebookLM (Playwright automation)
        └── Research Pipeline (combines all above)
```

**Response caching:** Built-in SQLite cache (`cache.py`) with configurable TTL. Same query won't hit Google twice within the cache window.

---

## 🛣️ Roadmap

- [x] Phase 1: YouTube, Trends, News, Scholar, Research Pipeline
- [x] Phase 2: Maps, Books, Patents, NotebookLM, YouTube Search
- [ ] Phase 3: Auto-research → NotebookLM → podcast → Telegram delivery
- [ ] Phase 4: Google Flights, Google Finance, Google Shopping
- [ ] pip install support (`pip install google-mcp-server`)

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 🤝 Contributing

PRs welcome! Each tool is a standalone module in `tools_*.py` — easy to add new ones.

To add a new Google service:
1. Create `tools_yourservice.py` with the scraping/API logic
2. Add the MCP tool wrapper in `server.py`
3. Add tests in `tests/test_tools.py`
4. Update this README

---

## 📄 License

MIT — use it however you want.
