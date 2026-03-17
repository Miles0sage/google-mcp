# Google MCP Server — Setup Guide

## Quick Install

```bash
git clone https://github.com/Miles0sage/google-mcp.git
cd google-mcp
pip install -r requirements.txt
```

## NotebookLM Authentication

NotebookLM tools require browser cookies. One-time setup:

```bash
# 1. Install notebooklm-py (already in requirements.txt)
pip install notebooklm-py

# 2. Authenticate — opens browser, you login to Google
python3 -m notebooklm auth

# This saves cookies to ~/.notebooklm/storage_state.json
# The tools use NotebookLMClient.from_storage() which reads this file
```

If `python3 -m notebooklm auth` doesn't work on headless VPS:
1. Run it on your local machine (Mac/Windows with browser)
2. Copy `~/.notebooklm/storage_state.json` to VPS at same path
3. Or set `NOTEBOOKLM_STORAGE_PATH=/path/to/storage_state.json`

## MCP Config

Add to `~/.mcp.json` (Claude Code) or your MCP client config:

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

## Tool Usage from Claude Code

Once configured, you can use tools like:

```
# YouTube
"Get transcript of this video: https://youtube.com/watch?v=..."
"Search YouTube for AI agent tutorials"

# Research
"Research the topic 'autonomous AI agents 2026' using research_pipeline"
"What's trending on Google for 'Claude AI'?"
"Find recent news about MCP servers"

# NotebookLM
"List my NotebookLM notebooks"
"Create a notebook called 'AI Research' with these URLs: url1, url2, url3"
"Add this YouTube video to notebook [ID]: https://youtube.com/watch?v=..."
"Generate a podcast for notebook [ID]"
"Ask notebook [ID]: What are the key findings?"

# Maps
"Search for barbershops in Flagstaff AZ" (needs GOOGLE_MAPS_API_KEY)

# Scholar
"Search Google Scholar for 'transformer architecture'" (may need proxy on VPS)
```

## Environment Variables

```bash
# Optional — only needed for specific tools
export GOOGLE_MAPS_API_KEY="your-key"        # For maps_search, maps_details
export PERPLEXITY_API_KEY="your-key"         # Enhanced research_pipeline
```

## Testing

```bash
python3 -m pytest tests/ -v
```

## How the AI Factory Workers Build This

The google-mcp server was built using Alibaba's coding plan workers:

```bash
# From /root/ai-factory, dispatch a task to build a tool module:
python3 factory.py alibaba_claude "Create /root/google-mcp/tools_youtube.py with..." qwen3-coder-plus --cwd /root/google-mcp

# Cost: ~$0.001 per module
# The worker writes the file, we wire it into server.py
# Total server cost to build: ~$0.012
```

This pattern works for adding any new Google service:
1. Dispatch to Alibaba worker with detailed prompt
2. Worker creates `tools_yourservice.py`
3. Add MCP tool wrappers in `server.py`
4. Test, commit, push
