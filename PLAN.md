# Google MCP — Open Source Google Services for AI Agents

## What
MCP server that gives AI agents access to Google services that have NO official API.
Wraps existing libraries + browser automation into one clean MCP interface.

## Services

### Phase 1 (MVP)
- **YouTube Transcripts** — grab any video transcript (youtube-transcript-api)
- **Google Trends** — trending topics, interest over time (pytrends)
- **NotebookLM** — create notebooks, add sources, generate podcasts (notebooklm-py)
- **Google Scholar** — search papers, get citations (scholarly/scraping)
- **Google News** — search news articles (gnews)

### Phase 2
- **Google Patents** — search patents (scraping)
- **Google Maps/Places** — search places, reviews (API key)
- **YouTube Search** — search videos, get metadata
- **Google Books** — search books, get previews

### Phase 3 — Research Pipeline
- Input: topic/question
- Auto-search across all sources
- Create NotebookLM notebook with findings
- Generate audio summary
- Output: structured report + citations + PDF

## Stack
- Python (FastAPI + MCP protocol)
- youtube-transcript-api, pytrends, notebooklm-py, scholarly
- MCP server (stdio or SSE)

## Auth
- NotebookLM: storage_state.json (browser cookies)
- GWS: OAuth tokens from gws CLI
- YouTube/Scholar/Trends: no auth needed (public)
