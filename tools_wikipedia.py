import urllib.request
import urllib.parse
import json
from typing import Dict, Any, List, Optional


def search_wikipedia(query: str, sentences: int = 5) -> str:
    """
    Search Wikipedia using the REST API and return formatted results.

    Args:
        query: Search query string
        sentences: Number of sentences to return in summary (default 5)

    Returns:
        Formatted string with search results
    """
    # Encode the query for URL
    encoded_query = urllib.parse.quote(query.strip())

    # First, try to get the summary page directly
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"

    try:
        req = urllib.request.Request(summary_url, headers={'User-Agent': 'Claude-Agent/1.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))

        # Check if this is a disambiguation page
        if data.get('type') == 'disambiguation':
            return _handle_disambiguation_page(data, query)

        # Extract the requested number of sentences from the extract
        extract = data.get('extract', '')
        if extract and sentences > 0:
            # Split extract into sentences and take the requested number
            sentences_list = extract.split('. ')
            if len(sentences_list) > sentences:
                extract = '. '.join(sentences_list[:sentences]) + '.'

        # Format the result
        result = f"Title: {data.get('title', 'N/A')}\n"
        result += f"Description: {data.get('description', 'N/A')}\n"
        result += f"Summary: {extract}\n"

        # Add thumbnail if available
        thumbnail = data.get('thumbnail')
        if thumbnail:
            result += f"Thumbnail: {thumbnail.get('source', 'N/A')}\n"

        # Add full article link
        content_urls = data.get('content_urls', {}).get('desktop', {})
        page_url = content_urls.get('page', 'N/A')
        result += f"Article URL: {page_url}\n"

        return result

    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Try the search API when direct lookup fails
            return _search_wikipedia_api(query)
        else:
            return f"Error accessing Wikipedia: {e}"
    except Exception as e:
        return f"Error processing Wikipedia data: {e}"


def _handle_disambiguation_page(data: Dict[str, Any], original_query: str) -> str:
    """Handle disambiguation pages by showing available options."""
    result = f"Disambiguation page for '{data.get('title', original_query)}'\n"
    result += "Possible matches:\n"

    pages = data.get('pages', [])
    for i, page in enumerate(pages[:5]):  # Limit to first 5 options
        title = page.get('title', 'N/A')
        extract = page.get('extract', 'N/A')
        result += f"{i+1}. {title}: {extract}\n"

    return result


def _search_wikipedia_api(query: str) -> str:
    """Use the search API when direct lookup fails."""
    encoded_query = urllib.parse.quote(query.strip())
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&format=json&srlimit=5"

    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Claude-Agent/1.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))

        search_results = data.get('query', {}).get('search', [])
        if not search_results:
            return f"No results found for '{query}'"

        result = f"Wikipedia search results for '{query}':\n"
        for i, item in enumerate(search_results):
            title = item.get('title', 'N/A')
            snippet = item.get('snippet', 'N/A')
            # Clean up the snippet
            snippet = snippet.replace('<span class="searchmatch">', '').replace('</span>', '')
            result += f"{i+1}. {title}\n   {snippet}\n"

        return result

    except Exception as e:
        return f"Error searching Wikipedia: {e}"