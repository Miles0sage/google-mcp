#!/usr/bin/env python3
"""
Google MCP Server
Exposes Google services as MCP tools using FastMCP
"""

from mcp.server.fastmcp import FastMCP
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, parse_qs
import io
import sys

# Import required libraries
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

try:
    from gnews import GNews
except ImportError:
    GNews = None

try:
    from scholarly import scholarly
except ImportError:
    scholarly = None


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                p = parse_qs(parsed_url.query)
                return p['v'][0]
            if parsed_url.path[:7] == '/embed/':
                return parsed_url.path.split('/')[2]
            if parsed_url.path[:3] == '/v/':
                return parsed_url.path.split('/')[2]
        # If none of the above conditions match, raise an exception
        raise ValueError(f"Invalid YouTube URL: {url}")
    except Exception as e:
        raise ValueError(f"Could not extract video ID from URL {url}: {str(e)}")


def _cached(tool_name: str, args: dict, fn, ttl: int = 3600):
    """Check cache, call fn if miss, store result."""
    try:
        from cache import cache_key, get_cached, set_cache
        key = cache_key(tool_name, **args)
        hit = get_cached(key)
        if hit is not None:
            return hit
        result = fn()
        set_cache(key, result, ttl_seconds=ttl)
        return result
    except Exception:
        return fn()


def create_server():
    mcp = FastMCP("google-mcp")

    @mcp.tool()
    def youtube_transcript(video_url: str, language: str = 'en') -> str:
        """
        Extract transcript from YouTube video.

        Args:
            video_url: URL of the YouTube video
            language: Language code for transcript (default: 'en')

        Returns:
            Transcript as a string
        """
        try:
            if YouTubeTranscriptApi is None:
                return "Error: youtube_transcript_api library not installed"

            video_id = extract_video_id(video_url)
            ytt = YouTubeTranscriptApi()
            transcript_list = ytt.fetch(video_id, languages=[language])
            transcript = ' '.join([snippet.text for snippet in transcript_list])
            return transcript
        except Exception as e:
            return f"Error retrieving transcript: {str(e)}"

    @mcp.tool()
    def google_trends(keyword: str, timeframe: str = 'today 3-m', geo: str = '') -> str:
        """
        Get Google Trends data for a keyword.

        Args:
            keyword: Keyword to search for
            timeframe: Time range (default: 'today 3-m')
            geo: Geographic location (default: '')

        Returns:
            Google Trends data as a formatted string
        """
        try:
            if TrendReq is None:
                return "Error: pytrends library not installed"

            pytrend = TrendReq(hl='en-US', tz=360)
            kw_list = [keyword]
            pytrend.build_payload(kw_list, timeframe=timeframe, geo=geo)
            interest_over_time_df = pytrend.interest_over_time()

            if interest_over_time_df.empty:
                return f"No trends data found for keyword: {keyword}"

            result = f"Google Trends data for '{keyword}' (timeframe: {timeframe}, geo: {geo}):\n"
            result += interest_over_time_df.to_string()
            return result
        except Exception as e:
            return f"Error retrieving Google Trends data: {str(e)}"

    @mcp.tool()
    def google_news(query: str, max_results: int = 10, language: str = 'en') -> str:
        """
        Search Google News for a query.

        Args:
            query: Search query
            max_results: Maximum number of results (default: 10)
            language: Language code (default: 'en')

        Returns:
            News articles as a formatted string
        """
        try:
            if GNews is None:
                return "Error: gnews library not installed"

            google_news = GNews(
                language=language,
                max_results=max_results
            )
            news_items = google_news.get_news(query)

            if not news_items:
                return f"No news articles found for query: {query}"

            result = f"Google News results for '{query}':\n"
            for i, item in enumerate(news_items, 1):
                result += f"\n{i}. {item.get('title', 'No Title')}\n"
                result += f"   Description: {item.get('description', 'No Description')}\n"
                result += f"   URL: {item.get('url', 'No URL')}\n"
                result += f"   Published Date: {item.get('published date', 'No Date')}\n"
            return result
        except Exception as e:
            return f"Error retrieving Google News: {str(e)}"

    @mcp.tool()
    def google_scholar(query: str, max_results: int = 5) -> str:
        """
        Search Google Scholar for academic papers.

        Args:
            query: Search query
            max_results: Maximum number of results (default: 5)

        Returns:
            Academic papers as a formatted string
        """
        try:
            if scholarly is None:
                return "Error: scholarly library not installed"

            import signal

            def _timeout_handler(signum, frame):
                raise TimeoutError("Scholar search timed out (rate-limited)")

            # Fail fast: 8 second timeout instead of 60+ seconds of retries
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(8)

            try:
                search_query = scholarly.search_pubs(query)
                results = []
                count = 0

                for pub in search_query:
                    if count >= max_results:
                        break
                    results.append(pub)
                    count += 1
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            if not results:
                return f"No academic papers found for query: {query}"

            result = f"Google Scholar results for '{query}':\n"
            for i, pub in enumerate(results, 1):
                result += f"\n{i}. {pub.get('bib', {}).get('title', 'No Title')}\n"
                result += f"   Author(s): {pub.get('bib', {}).get('author', 'Unknown')}\n"
                result += f"   Year: {pub.get('bib', {}).get('pub_year', 'Unknown')}\n"
                result += f"   Abstract: {pub.get('bib', {}).get('abstract', 'No Abstract')}\n"
                result += f"   URL: {pub.get('eprint_url', pub.get('pub_url', 'No URL'))}\n"
                result += f"   Citations: {pub.get('num_citations', 0)}\n"
            return result
        except Exception as e:
            return f"Error retrieving Google Scholar data: {str(e)}"

    @mcp.tool()
    def research_pipeline(topic: str, max_sources: int = 10) -> str:
        """
        Combined research pipeline across multiple sources.

        Args:
            topic: Research topic
            max_sources: Maximum number of sources per category (default: 10)

        Returns:
            Combined research report as a formatted string
        """
        try:
            result = f"Research Pipeline Report for: {topic}\n"
            result += "=" * 50 + "\n\n"

            # News Section
            result += "NEWS ARTICLES:\n"
            result += "-" * 20 + "\n"
            try:
                news_results = google_news(query=topic, max_results=max_sources, language='en')
                result += news_results + "\n\n"
            except Exception as e:
                result += f"Error retrieving news: {str(e)}\n\n"

            # Academic Papers Section
            result += "ACADEMIC PAPERS:\n"
            result += "-" * 20 + "\n"
            try:
                scholar_results = google_scholar(query=topic, max_results=max_sources)
                result += scholar_results + "\n\n"
            except Exception as e:
                result += f"Error retrieving academic papers: {str(e)}\n\n"

            # Trend Data Section
            result += "TREND DATA:\n"
            result += "-" * 20 + "\n"
            try:
                trends_results = google_trends(keyword=topic, timeframe='today 3-m', geo='')
                result += trends_results
            except Exception as e:
                result += f"Error retrieving trends: {str(e)}"

            return result
        except Exception as e:
            return f"Error in research pipeline: {str(e)}"

    # -----------------------------------------------------------------------
    # Phase 2 tools — Maps, YouTube Search, Books, Patents, NotebookLM
    # -----------------------------------------------------------------------

    @mcp.tool()
    def maps_search(query: str, location: str = '', radius: int = 5000) -> str:
        """Search Google Maps for places (restaurants, barbershops, etc).
        Args:
            query: What to search for (e.g. "barbershops in Flagstaff AZ")
            location: Center point as "lat,lng" (optional)
            radius: Search radius in meters (default 5000)
        """
        try:
            from tools_maps import search_places
            return search_places(query, location, radius)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def maps_details(place_id: str) -> str:
        """Get detailed info for a Google Maps place (reviews, hours, phone, website).
        Args:
            place_id: Google Maps place ID from maps_search results
        """
        try:
            from tools_maps import place_details
            return place_details(place_id)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def youtube_search(query: str, max_results: int = 10) -> str:
        """Search YouTube for videos by keyword.
        Args:
            query: Search query
            max_results: Max videos to return (default 10)
        """
        try:
            from tools_youtube import search_youtube
            return search_youtube(query, max_results)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def youtube_channel(channel_url: str, max_results: int = 10) -> str:
        """Get recent videos from a YouTube channel.
        Args:
            channel_url: YouTube channel URL
            max_results: Max videos to return (default 10)
        """
        try:
            from tools_youtube import channel_videos
            return channel_videos(channel_url, max_results)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def books_search(query: str, max_results: int = 5) -> str:
        """Search Google Books for books by keyword.
        Args:
            query: Book search query
            max_results: Max results (default 5)
        """
        try:
            from tools_books import search_books
            return search_books(query, max_results)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def patents_search(query: str, max_results: int = 5) -> str:
        """Search Google Patents for patents by keyword.
        Args:
            query: Patent search query
            max_results: Max results (default 5)
        """
        try:
            from tools_patents import search_patents
            return search_patents(query, max_results)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def notebooklm_list() -> str:
        """List all your NotebookLM notebooks."""
        try:
            from tools_notebooklm import list_notebooks
            return list_notebooks()
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def notebooklm_create(title: str, source_urls: str) -> str:
        """Create a NotebookLM notebook and add source URLs.
        Args:
            title: Notebook title
            source_urls: Comma-separated list of URLs to add as sources
        """
        try:
            from tools_notebooklm import create_notebook
            urls = [u.strip() for u in source_urls.split(',') if u.strip()]
            return create_notebook(title, urls)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def notebooklm_add_source(notebook_id: str, url: str) -> str:
        """Add a URL source to an existing NotebookLM notebook.
        Args:
            notebook_id: Notebook ID from notebooklm_list
            url: URL to add as source
        """
        try:
            from tools_notebooklm import add_source
            return add_source(notebook_id, url)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def notebooklm_add_youtube(notebook_id: str, youtube_url: str) -> str:
        """Add a YouTube video as a source to a NotebookLM notebook.
        Args:
            notebook_id: Notebook ID
            youtube_url: YouTube video URL
        """
        try:
            from tools_notebooklm import add_youtube_source
            return add_youtube_source(notebook_id, youtube_url)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def notebooklm_add_text(notebook_id: str, title: str, text: str) -> str:
        """Add text/paste content as a source to a NotebookLM notebook.
        Args:
            notebook_id: Notebook ID
            title: Source title
            text: Text content to add
        """
        try:
            from tools_notebooklm import add_text_source
            return add_text_source(notebook_id, title, text)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def notebooklm_podcast(notebook_id: str) -> str:
        """Generate an Audio Overview (podcast) for a NotebookLM notebook.
        Args:
            notebook_id: Notebook ID from notebooklm_list
        """
        try:
            from tools_notebooklm import generate_podcast
            return generate_podcast(notebook_id)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def notebooklm_ask(notebook_id: str, question: str) -> str:
        """Ask a question to a NotebookLM notebook's sources. Get AI-generated answer grounded in the sources.
        Args:
            notebook_id: Notebook ID
            question: Question to ask
        """
        try:
            from tools_notebooklm import ask_notebook
            return ask_notebook(notebook_id, question)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def notebooklm_sources(notebook_id: str) -> str:
        """List all sources in a NotebookLM notebook.
        Args:
            notebook_id: Notebook ID
        """
        try:
            from tools_notebooklm import notebook_sources
            return notebook_sources(notebook_id)
        except Exception as e:
            return f"Error: {e}"

    # -----------------------------------------------------------------------
    # Phase 3 tools — Wikipedia, Webpage, arXiv, Translate, Finance
    # -----------------------------------------------------------------------

    @mcp.tool()
    def wikipedia(query: str) -> str:
        """Search Wikipedia and get article summary.
        Args:
            query: Topic to search (e.g. 'machine learning', 'Model Context Protocol')
        """
        try:
            from tools_wikipedia import search_wikipedia
            return search_wikipedia(query)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def webpage_read(url: str, max_chars: int = 5000) -> str:
        """Extract main text content from any webpage URL. Strips HTML, scripts, styles.
        Args:
            url: URL to read
            max_chars: Max characters to return (default 5000)
        """
        try:
            from tools_webpage import extract_webpage
            return extract_webpage(url, max_chars)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def arxiv_search(query: str, max_results: int = 5) -> str:
        """Search arXiv for academic papers (free, no API key).
        Args:
            query: Search query (e.g. 'transformer attention mechanism')
            max_results: Max papers to return (default 5)
        """
        try:
            from tools_arxiv import search_arxiv
            return search_arxiv(query, max_results)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def arxiv_paper(arxiv_id: str) -> str:
        """Get full details of an arXiv paper by ID (abstract, authors, categories).
        Args:
            arxiv_id: arXiv paper ID (e.g. '2309.07864')
        """
        try:
            from tools_arxiv import get_paper
            return get_paper(arxiv_id)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def translate(text: str, target_language: str = 'en', source_language: str = 'auto') -> str:
        """Translate text between languages using Google Translate (free, no API key).
        Args:
            text: Text to translate
            target_language: Target language code (e.g. 'es', 'fr', 'de', 'zh', 'ja', 'ar')
            source_language: Source language code or 'auto' to detect
        """
        try:
            from tools_translate import translate_text
            return translate_text(text, target_language, source_language)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def stock_quote(symbol: str) -> str:
        """Get real-time stock quote (price, change, market cap, PE ratio, 52-week range).
        Args:
            symbol: Stock ticker symbol (e.g. 'AAPL', 'GOOGL', 'TSLA')
        """
        try:
            from tools_finance import stock_quote as _sq
            return _sq(symbol)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def market_overview() -> str:
        """Get major market indices overview (S&P 500, NASDAQ, DOW)."""
        try:
            from tools_finance import market_overview as _mo
            return _mo()
        except Exception as e:
            return f"Error: {e}"

    return mcp


if __name__ == '__main__':
    mcp = create_server()
    mcp.run()