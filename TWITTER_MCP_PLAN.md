# Twitter/X MCP Server — Build Plan

## Why Build Our Own
- Official X API: $100/mo minimum (Basic), $5K/mo (Pro)
- Existing Twitter MCPs: all require API keys
- Our approach: Playwright browser automation (like NotebookLM) — FREE

## Architecture
Same pattern as google-mcp: Python + FastMCP + browser automation via Playwright

## Tools to Build

### Reading (no auth needed for public)
1. `twitter_search(query, max_results=10)` — search tweets by keyword
2. `twitter_user(username)` — get user profile (bio, followers, following, tweet count)
3. `twitter_user_tweets(username, max_results=10)` — get recent tweets from a user
4. `twitter_trending(location='US')` — get trending topics
5. `twitter_thread(tweet_url)` — get full thread from a tweet URL

### Writing (needs auth via cookies)
6. `twitter_post(text)` — post a tweet
7. `twitter_reply(tweet_url, text)` — reply to a tweet
8. `twitter_like(tweet_url)` — like a tweet
9. `twitter_retweet(tweet_url)` — retweet
10. `twitter_dm(username, text)` — send DM

### Analytics
11. `twitter_feed(max_results=20)` — read your home feed (For You / Following)
12. `twitter_notifications()` — read notifications/mentions

## Auth
- Use Playwright with saved cookies (same as NotebookLM)
- `twitter login` CLI command opens browser, user logs in, cookies saved
- Keepalive cron every 30 min (same pattern)
- Storage: `~/.twitter-mcp/storage_state.json`

## Stack
- `tools_twitter.py` — all 12 functions using Playwright
- Wire into `server.py` as 12 MCP tools
- No external deps beyond playwright

## Reading Without Auth (scraping fallback)
For search and public profiles, can use:
- Nitter instances (public Twitter mirrors)
- Direct scraping of twitter.com with Playwright headless
- syndication.twitter.com API (some endpoints still work without auth)

## Build Order
1. Read tools first (search, user, trending) — no auth needed
2. Test thoroughly
3. Add write tools (post, reply) — needs cookie auth
4. Add feed/notifications — needs cookie auth

## Estimated Build Time
- 2 hours with Alibaba workers
- Each tool module dispatched separately
- Integration + testing: 30 min

## Decision: Standalone or Add to google-mcp?
STANDALONE repo: `twitter-mcp` — separate from google-mcp because:
- Different auth mechanism
- Different risk profile (Twitter blocks bots aggressively)
- Standalone gets its own stars
- Can be installed independently
