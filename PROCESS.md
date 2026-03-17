# Google MCP + AI Factory + NotebookLM — Complete Process Guide

> For any Claude Code instance running on this VPS (`v2202602335740431780.megasrv.de`)

---

## 1. Where Everything Lives

```
/root/ai-factory/          AI Factory — multi-model task dispatcher
/root/google-mcp/          Google MCP Server — 19 tools for unofficial Google services
/root/openclaw/            OpenClaw — PA, gateway, agents (63+ MCP tools)
/root/.mcp.json            MCP server config (all servers registered here)
/root/.notebooklm/         NotebookLM auth cookies (storage_state.json)
/root/.config/gmail/       Google OAuth tokens (Calendar + Gmail)
```

## 2. MCP Servers Available

These are pre-configured in `/root/.mcp.json`. Claude Code loads them automatically:

| Server | Name in config | Tools | What it does |
|--------|---------------|-------|-------------|
| AI Factory | `ai-factory` | 12 | Dispatch tasks to 8 AI workers, swarm debates, memory |
| Google Research | `google-research` | 19 | YouTube, Trends, News, Scholar, NotebookLM, Maps |
| OpenClaw | `openclaw` | 63 | PA tools, betting, research, coding, memory |
| Supabase | `supabase` | SQL, migrations | Direct database access |
| GitHub | `github` | PRs, issues, code search | GitHub API |
| Perplexity | `perplexity` | Search, reason, deep research | Web research |
| Exa | `exa` | Advanced web search | Deep web search |
| Playwright | `playwright` | Browser automation | Web scraping, testing |
| Context7 | `context7` | Library docs | Up-to-date API docs |

## 3. How to Use AI Factory

### Direct dispatch (cheap workers do the work):
```bash
cd /root/ai-factory

# Use Alibaba (cheapest, $0.001/task, flat-rate):
python3 factory.py alibaba_claude "Write a Python function to sort a list" qwen3-coder-plus --cwd /root/some-project

# Use Alibaba direct API (even cheaper, no file editing):
python3 factory.py alibaba "Explain how transformers work" qwen3-coder-plus

# Smart routing (orchestrator picks best worker):
python3 orchestrator.py "Fix the auth bug in login.py" --cwd /root/my-project

# Swarm debate (43 agents deliberate):
python3 factory.py swarm "Should we use PostgreSQL or MongoDB for this project?"
```

### From MCP tools in Claude Code:
```
Use the factory_dispatch tool: "Write tests for auth.py"
Use the factory_swarm tool: "Debate: microservices vs monolith"
Use the factory_build tool: "Fix the login bug" with cwd=/root/project
```

### Via Supabase task queue (async, from anywhere):
```bash
python3 task_queue.py push "Build landing page" --type feature --priority 7
python3 task_queue.py process  # daemon picks up and runs
python3 task_queue.py watch --interval 30  # watch mode
```

### Available workers:
| Worker | CLI name | Model | Cost |
|--------|----------|-------|------|
| Claude Code | `claude_code` | haiku/sonnet/opus | $0.10/min |
| Alibaba Claude | `alibaba_claude` | qwen3-coder-plus | $0.001/min (flat) |
| MiniMax Claude | `minimax_claude` | MiniMax-M2.5 | $0.001/min (flat) |
| Codex | `codex` | GPT-5 | $0.02/min |
| Alibaba Direct | `alibaba` | qwen3-coder-plus | $0.001/min |
| MiniMax Direct | `minimax` | MiniMax-M2.5 | $0.001/min |
| Aider | `aider` | varies | free |
| Swarm | `swarm` | 43 agents | $0.003/min |

**Rule: Use `alibaba_claude` or `alibaba` for 90% of tasks. Only use `claude_code` for complex multi-file work.**

## 4. How to Use Google MCP (19 tools)

### YouTube tools:
```bash
# Get transcript of any video
# Tool: youtube_transcript
# Args: {"video_url": "https://youtube.com/watch?v=VIDEO_ID"}

# Search YouTube
# Tool: youtube_search
# Args: {"query": "AI agents tutorial", "max_results": 5}

# Get channel videos
# Tool: youtube_channel
# Args: {"channel_url": "https://youtube.com/@channel", "max_results": 10}
```

### Research tools:
```bash
# Google News (real-time)
# Tool: google_news
# Args: {"query": "MCP server AI", "max_results": 5}

# Google Trends
# Tool: google_trends
# Args: {"keyword": "Claude AI", "timeframe": "today 3-m"}

# Google Scholar (may 429 on VPS — works locally)
# Tool: google_scholar
# Args: {"query": "transformer architecture", "max_results": 5}

# Google Books (free API)
# Tool: books_search
# Args: {"query": "machine learning", "max_results": 5}

# Combined research (News + Scholar + Trends + YouTube in one call)
# Tool: research_pipeline
# Args: {"topic": "autonomous AI agents", "max_sources": 5}
```

### NotebookLM tools (requires auth — see Section 5):
```bash
# List notebooks
# Tool: notebooklm_list
# Args: {}

# Create notebook with sources
# Tool: notebooklm_create
# Args: {"title": "My Research", "source_urls": "https://url1.com,https://url2.com"}

# Add URL source to notebook
# Tool: notebooklm_add_source
# Args: {"notebook_id": "NOTEBOOK_ID", "url": "https://example.com/article"}

# Add YouTube video as source
# Tool: notebooklm_add_youtube
# Args: {"notebook_id": "NOTEBOOK_ID", "youtube_url": "https://youtube.com/watch?v=..."}

# Add raw text as source
# Tool: notebooklm_add_text
# Args: {"notebook_id": "NOTEBOOK_ID", "title": "My Notes", "text": "Content here..."}

# Generate podcast (Audio Overview)
# Tool: notebooklm_podcast
# Args: {"notebook_id": "NOTEBOOK_ID"}

# Ask questions grounded in sources
# Tool: notebooklm_ask
# Args: {"notebook_id": "NOTEBOOK_ID", "question": "What are the key findings?"}

# List sources in notebook
# Tool: notebooklm_sources
# Args: {"notebook_id": "NOTEBOOK_ID"}
```

### Maps tools (requires GOOGLE_MAPS_API_KEY in env):
```bash
# Search places
# Tool: maps_search
# Args: {"query": "barbershops in Flagstaff AZ"}

# Get place details
# Tool: maps_details
# Args: {"place_id": "PLACE_ID_FROM_SEARCH"}
```

## 5. NotebookLM Authentication Setup

NotebookLM uses Google cookies, not OAuth. One-time setup:

### Option A: On a machine with a browser (Mac/Windows)
```bash
pip install notebooklm-py
python3 -m notebooklm auth
# Browser opens → login to Google → cookies saved to ~/.notebooklm/
# Copy the file to VPS:
scp ~/.notebooklm/storage_state.json root@YOUR_VPS:~/.notebooklm/
```

### Option B: On VPS with existing Playwright cookies
```bash
# If you already have Playwright storage_state.json from notebooklm.google.com:
mkdir -p ~/.notebooklm
cp /path/to/your/storage_state.json ~/.notebooklm/storage_state.json
```

### Check if auth works:
```bash
cd /root/google-mcp
python3 -c "
from tools_notebooklm import list_notebooks
print(list_notebooks())
"
```

## 6. Deep Research Agent v2

Full autonomous research pipeline at `/root/ai-factory/deep_research_v2.py`:

```bash
cd /root/ai-factory

# Basic research
python3 deep_research_v2.py "What are the best AI agent frameworks in 2026?"

# Technical mode with budget
python3 deep_research_v2.py "Compare STORM vs GPT-Researcher architecture" --mode technical --time 120

# Market research
python3 deep_research_v2.py "Barbershop software market size 2026" --mode market
```

### How it works:
1. **Decompose**: Alibaba API breaks topic into 5 sub-questions ($0.00)
2. **Gather**: Searches YouTube + News + Trends + Perplexity in parallel ($0.00)
3. **Synthesize**: Alibaba API creates structured report with confidence score ($0.00)
4. **Total cost**: ~$0.00 per research task (all free sources)

## 7. Full Research → NotebookLM → Podcast Workflow

This is the killer workflow. End-to-end:

```bash
# Step 1: Run deep research
cd /root/ai-factory
python3 deep_research_v2.py "autonomous AI agents 2026" --mode technical > /tmp/research_output.md

# Step 2: Create NotebookLM notebook with the research + source URLs
cd /root/google-mcp
python3 -c "
from tools_notebooklm import create_notebook, add_text_source, generate_podcast
import json

# Create notebook
result = create_notebook('AI Agents Research 2026', [
    'https://arxiv.org/abs/2309.07864',  # AutoGen paper
    'https://arxiv.org/abs/2308.08155',  # STORM paper
])
print(result)
# Get notebook ID from result, then:

# Add the deep research output as text source
# add_text_source('NOTEBOOK_ID', 'Deep Research Output', open('/tmp/research_output.md').read())

# Generate podcast
# generate_podcast('NOTEBOOK_ID')
"

# Step 3: Podcast generates in 2-5 minutes on Google's servers (free)
# Step 4: Listen on notebooklm.google.com or download audio
```

## 8. GWS (Google Workspace) — Calendar + Gmail

Already working through the gateway:

```bash
# Read today's calendar
curl -s http://localhost:18789/api/calendar/today | python3 -m json.tool

# Create calendar event
curl -s -X POST http://localhost:18789/api/calendar/create \
  -H "Content-Type: application/json" \
  -d '{"summary":"Meeting","start":"2026-03-18T10:00:00-07:00","end":"2026-03-18T10:30:00-07:00"}'

# Read Gmail inbox
curl -s "http://localhost:18789/api/gmail/inbox?limit=5" | python3 -m json.tool

# Send email
curl -s -X POST http://localhost:18789/api/gmail/send \
  -H "Content-Type: application/json" \
  -d '{"to":"someone@gmail.com","subject":"Hello","body":"Email body here"}'
```

The PA on Cloudflare (`pa.overseerclaw.uk`) has `create_event` and `send_email` tools that call these gateway endpoints from Telegram.

## 9. Troubleshooting

### "MCP tools not showing up"
- Restart Claude Code session (tools load on startup from `~/.mcp.json`)
- Check server starts: `cd /root/google-mcp && python3 server.py` (should hang = working)

### "NotebookLM auth failed"
- Re-run `python3 -m notebooklm auth` on a machine with browser
- Copy `~/.notebooklm/storage_state.json` to VPS
- Cookies expire — re-auth monthly

### "Google Scholar 429 rate limited"
- Normal on VPS IPs — Google blocks automated scraping
- Works fine from residential IPs / local machine
- Use Perplexity or Exa for academic search as fallback

### "AI Factory task didn't produce output"
- Check logs: `ls /root/ai-factory/data/logs/`
- The worker may have hit the model's context limit
- Try shorter prompts or use `alibaba` (direct API) instead of `alibaba_claude` (headless)

### "Can't call tools from another Claude instance"
- That instance needs to be running ON this VPS (SSH in)
- Or install google-mcp locally on that machine
- MCP servers are local processes, not remote APIs

## 10. Key API Keys & Tokens (already set)

All in `/root/ai-factory/.env` and `/root/openclaw/.env`:
- `ALIBABA_CODING_API_KEY` — Alibaba flat-rate coding plan
- `MINIMAX_API_KEY` — MiniMax M2.5
- `PERPLEXITY_API_KEY` — Perplexity Sonar
- `TELEGRAM_BOT_TOKEN` — PA Telegram bot
- Google OAuth — `/root/.config/gmail/token.json` (auto-refreshes)
- NotebookLM — `~/.notebooklm/storage_state.json`
