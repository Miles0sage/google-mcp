import urllib.request
import urllib.parse
import json
import re
from typing import Dict, List, Optional


def search_patents(query: str, max_results: int = 5) -> str:
    """
    Search for patents using Google Patents.

    Args:
        query: Search query for patents
        max_results: Maximum number of results to return (default 5)

    Returns:
        Formatted string with patent search results
    """
    try:
        # First, try the Google Patents XHR API approach
        encoded_query = urllib.parse.quote(query)
        xhr_url = f"https://patents.google.com/xhr/query?url=q%3D{encoded_query}&num={max_results}"

        req = urllib.request.Request(
            xhr_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://patents.google.com/',
                'Accept': 'application/json',
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

            if 'results' in data and data['results']:
                return _format_patent_results(data['results'], max_results)

        # If XHR API fails, try scraping the main patents page
        search_url = f"https://patents.google.com/?q={encoded_query}"
        req = urllib.request.Request(
            search_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')

        # Parse HTML with regex to extract patent information
        return _parse_patent_html(html, max_results)

    except Exception as e:
        # If Google Patents fails, try Lens.org API as fallback
        try:
            return _search_lens_api(query, max_results)
        except Exception as lens_error:
            return f"Error searching patents: {str(e)}\nLens.org fallback also failed: {str(lens_error)}"


def _format_patent_results(results: List[Dict], max_results: int) -> str:
    """Format patent results from Google Patents API."""
    if not results:
        return "No patents found."

    output = []
    for i, result in enumerate(results[:max_results], 1):
        publication_info = result.get('publication_info', {})
        title = result.get('title', 'N/A')
        publication_number = publication_info.get('publication_number', 'N/A')
        assignee = ', '.join(result.get('assignee', [])) if result.get('assignee') else 'N/A'
        filing_date = publication_info.get('filing_date', 'N/A')
        abstract = result.get('abstract', 'N/A')[:200] + "..." if len(result.get('abstract', '')) > 200 else result.get('abstract', 'N/A')

        output.append(f"{i}. Title: {title}")
        output.append(f"   Patent Number: {publication_number}")
        output.append(f"   Assignee: {assignee}")
        output.append(f"   Filing Date: {filing_date}")
        output.append(f"   Abstract: {abstract}")
        output.append("")

    return "\n".join(output)


def _parse_patent_html(html: str, max_results: int) -> str:
    """Parse patent information from Google Patents HTML using regex."""
    # Extract patent details using regex patterns
    # This is a simplified approach to extract patent titles, numbers, etc.
    title_pattern = r'<meta property="og:title" content="(.*?)"/>'
    titles = re.findall(title_pattern, html)

    # More complex patterns to extract patent details
    patent_details_pattern = r'data-id="(.*?)"[^>]*?>.*?<h3 class="[^"]*?">([^<]*?)</h3>'
    details_matches = re.findall(patent_details_pattern, html, re.DOTALL)

    if not titles and not details_matches:
        # Try alternative patterns for extracting patent information
        alt_title_pattern = r'<div class="[^"]*?result[^"]*?">.*?<a[^>]*?>([^<]*?)</a>'
        titles = re.findall(alt_title_pattern, html, re.DOTALL)

    if titles or details_matches:
        output = []
        results_count = min(max_results, len(titles) if titles else len(details_matches))

        for i in range(results_count):
            if titles:
                output.append(f"{i+1}. Title: {titles[i][:200] if len(titles[i]) > 200 else titles[i]}")
            elif details_matches:
                patent_id, title = details_matches[i]
                output.append(f"{i+1}. Title: {title[:200] if len(title) > 200 else title}")
                output.append(f"   Patent ID: {patent_id}")
            output.append("")

        return "\n".join(output)

    return "Could not extract patent information from the page."


def _search_lens_api(query: str, max_results: int) -> str:
    """Search patents using Lens.org API as a fallback."""
    try:
        # Prepare the query for Lens API
        payload = {
            "query": {
                "term": query
            },
            "size": max_results
        }

        req = urllib.request.Request(
            "https://api.lens.org/patent/search",
            data=json.dumps(payload).encode(),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

            if 'hits' in data and data['hits']:
                return _format_lens_results(data['hits'])

        return "No patents found via Lens.org API."

    except Exception as e:
        return f"Error querying Lens.org API: {str(e)}"


def _format_lens_results(hits: List[Dict]) -> str:
    """Format results from Lens.org API."""
    output = []
    for i, hit in enumerate(hits, 1):
        patent = hit.get('_source', {})
        title = patent.get('patent_title', 'N/A')
        doc_number = patent.get('lens_id', 'N/A')
        assignee = ', '.join(patent.get('applicant', [])) if patent.get('applicant') else 'N/A'
        pub_date = patent.get('publication_date', 'N/A')

        output.append(f"{i}. Title: {title}")
        output.append(f"   Patent Number: {doc_number}")
        output.append(f"   Assignee: {assignee}")
        output.append(f"   Publication Date: {pub_date}")
        output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    results = search_patents("machine learning", 3)
    print(results)