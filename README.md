# google-mcp

**27 tools. One MCP server. The entire Google research stack.**

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)
![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-brightgreen.svg)
![Tools](https://img.shields.io/badge/Tools-27-orange.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

The only MCP server that wraps Google services with **no official API** into clean, cacheable tools. YouTube transcripts, Google Scholar, NotebookLM automation, Trends, News, Maps, Finance, arXiv, Patents, Books, Translate, Wikipedia -- all from one `server.py`.

**21 of 27 tools are completely free. No API keys.**

---

## Quick Start

```bash
git clone https://github.com/Miles0sage/google-mcp.git
cd google-mcp
pip install -r requirements.txt
python3 server.py
```

That's it. The server runs on stdio and works with any MCP client.

---

## MCP Config

Add to `~/.mcp.json` (Claude Code) or your client's MCP config:

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

Docker:

```bash
docker build -t google-mcp .
docker run -it google-mcp
```

---

## All 27 Tools

### YouTube (3 tools)

| Tool | Description | Auth |
|------|-------------|------|
| `youtube_transcript` | Extract full transcript from any video | Free |
| `youtube_search` | Search videos by keyword | Free |
| `youtube_channel` | Get recent videos from a channel | Free |

### NotebookLM (9 tools) -- *No other MCP server has this*

| Tool | Description | Auth |
|------|-------------|------|
| `notebooklm_list` | List all notebooks | Browser |
| `notebooklm_create` | Create notebook + add URL sources | Browser |
| `notebooklm_add_source` | Add URL to existing notebook | Browser |
| `notebooklm_add_youtube` | Add YouTube video as source | Browser |
| `notebooklm_add_text` | Add text/paste as source | Browser |
| `notebooklm_podcast` | Generate Audio Overview (podcast) | Browser |
| `notebooklm_video` | Generate Cinematic Video Overview | Browser |
| `notebooklm_ask` | Ask questions with cited answers | Browser |
| `notebooklm_sources` | List sources in a notebook | Browser |

### Academic Research (4 tools)

| Tool | Description | Auth |
|------|-------------|------|
| `google_scholar` | Search papers, citations, abstracts | Free |
| `arxiv_search` | Search arXiv papers | Free |
| `arxiv_paper` | Full paper details by ID | Free |
| `research_pipeline` | Multi-source research in one call | Free |

### Google Services (6 tools)

| Tool | Description | Auth |
|------|-------------|------|
| `google_trends` | Interest over time, trending topics | Free |
| `google_news` | Real-time news search | Free |
| `books_search` | Search Google Books | Free |
| `patents_search` | Search Google Patents | Free |
| `maps_search` | Search places, restaurants, businesses | API Key |
| `maps_details` | Reviews, hours, phone, website | API Key |

### Finance (2 tools)

| Tool | Description | Auth |
|------|-------------|------|
| `stock_quote` | Real-time price, PE, 52-week range | Free |
| `market_overview` | S&P 500, NASDAQ, DOW snapshot | Free |

### Utilities (3 tools)

| Tool | Description | Auth |
|------|-------------|------|
| `translate` | 100+ languages via Google Translate | Free |
| `wikipedia` | Article summaries and search | Free |
| `webpage_read` | Extract text from any URL | Free |

---

## The Killer Feature: NotebookLM Automation

No other MCP server can do this:

```
"Create a notebook about AI agents and generate a podcast"

1. notebooklm_create("AI Agents Research", "url1,url2,url3")
2. notebooklm_add_youtube(id, "https://youtube.com/watch?v=...")
3. notebooklm_podcast(id)        --> Audio Overview generating
4. notebooklm_ask(id, "Key findings?")  --> Cited answer
```

Programmatic NotebookLM: create notebooks, add sources, generate podcasts and videos, ask questions -- all through MCP.

---

## vs scholar-mcp

| | **google-mcp** | scholar-mcp |
|---|---|---|
| **Total tools** | **27** | 7 |
| Google Scholar | Yes | Yes |
| arXiv | Yes | Yes |
| YouTube transcripts | Yes | No |
| YouTube search | Yes | No |
| NotebookLM (9 tools) | **Yes** | No |
| Google Trends | Yes | No |
| Google News | Yes | No |
| Google Maps | Yes | No |
| Google Finance | Yes | No |
| Google Books | Yes | No |
| Google Patents | Yes | No |
| Google Translate | Yes | No |
| Wikipedia | Yes | No |
| Webpage reader | Yes | No |
| Research pipeline | Yes | No |
| Response caching | **SQLite with TTL** | No |
| Docker support | Yes | No |

scholar-mcp does academic search well. google-mcp does academic search **plus 20 more tools** across the entire Google ecosystem.

---

## Examples

**YouTube transcript:**
```
youtube_transcript({"video_url": "https://youtube.com/watch?v=jGwO_UgTS7I"})
--> Full CS229 lecture transcript (69,877 chars)
```

**Multi-source research (one call):**
```
research_pipeline({"topic": "autonomous AI agents"})
--> NEWS + ACADEMIC PAPERS + TRENDS combined
```

**Stock quote:**
```
stock_quote({"symbol": "NVDA"})
--> $142.50 | +2.3% | PE 35.2 | 52w: $78.40 - $153.20
```

---

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_MAPS_API_KEY` | Maps tools only | [Google Cloud Console](https://console.cloud.google.com) ($200/mo free credit) |
| `PERPLEXITY_API_KEY` | Optional | Enhances `research_pipeline` with Perplexity Sonar |
| `NOTEBOOKLM_STORAGE_STATE` | NotebookLM tools | Path to Playwright browser cookies |

Everything else works out of the box. No keys, no OAuth, no setup.

---

## Architecture

```
MCP Client (Claude Code / Cursor / Windsurf)
    |
    v
google-mcp server (stdio)
    |
    |-- YouTube ............. youtube-transcript-api, scrapetube
    |-- NotebookLM ......... Playwright browser automation
    |-- Google Scholar ..... scholarly
    |-- Google Trends ...... pytrends
    |-- Google News ........ gnews
    |-- Google Maps ........ googlemaps
    |-- Google Finance ..... yfinance
    |-- arXiv .............. arxiv API
    |-- Google Books ....... Google Books API (free)
    |-- Google Patents ..... scraping
    |-- Translate .......... deep-translator
    |-- Wikipedia .......... wikipedia-api
    |-- Webpage ............ BeautifulSoup
    |
    +-- SQLite cache (configurable TTL, same query never hits Google twice)
```

---

## Contributing

Each tool lives in its own `tools_*.py` module. Adding a new Google service:

1. Create `tools_yourservice.py`
2. Add the MCP tool wrapper in `server.py`
3. Add tests in `tests/`
4. Submit PR

```bash
pytest tests/ -v
```

---

## License

MIT
