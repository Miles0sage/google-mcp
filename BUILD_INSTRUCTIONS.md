# Google MCP — Build Instructions for VPS Agent

## Setup
```bash
cd /root/google-mcp
python3 -m venv venv
source venv/bin/activate
pip install mcp youtube-transcript-api pytrends scholarly gnews notebooklm-py
```

## What to Build
A Python MCP server exposing these tools:
1. `youtube_transcript` — get transcript from any YouTube URL
2. `google_trends` — search trends, interest over time
3. `google_scholar` — search academic papers
4. `google_news` — search news articles
5. `notebooklm_create` — create notebook + add sources
6. `notebooklm_podcast` — generate audio summary
7. `research_pipeline` — full auto-research: topic → sources → report

## Auth Already on VPS
- NotebookLM: /root/.notebooklm/storage_state.json
- GWS: /root/.config/gws/ (OAuth tokens)

## MCP Protocol
- Use `mcp` pip package (official Anthropic Python SDK)
- Expose over stdio for Claude Code
- Register each tool with @server.tool() decorator

## Run
```bash
source /root/google-mcp/venv/bin/activate
python server.py
```
