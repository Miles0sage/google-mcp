"""Google Patents search via SerpAPI-free approach (scraping Google search)."""

import urllib.request
import urllib.parse
import json
import re


def search_patents(query: str, max_results: int = 5) -> str:
    """Search Google Patents by querying Google search with site:patents.google.com."""
    try:
        # Use Google search with site: filter — more reliable than scraping patents.google.com directly
        encoded = urllib.parse.quote(f"site:patents.google.com {query}")
        url = f"https://www.google.com/search?q={encoded}&num={max_results}"

        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })

        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Extract results from Google search HTML
        # Pattern: <h3 class="...">TITLE</h3> near patents.google.com URLs
        results = []

        # Find patent links and titles
        pattern = r'<a href="(https?://patents\.google\.com/patent/[^"]+)"[^>]*>.*?<h3[^>]*>(.*?)</h3>'
        matches = re.findall(pattern, html, re.DOTALL)

        if not matches:
            # Fallback: look for /url?q= redirects
            pattern2 = r'/url\?q=(https?://patents\.google\.com/patent/[^&"]+)[^>]*>.*?<h3[^>]*>(.*?)</h3>'
            matches = re.findall(pattern2, html, re.DOTALL)

        if not matches:
            # Last fallback: just find patent IDs
            patent_ids = re.findall(r'patents\.google\.com/patent/([A-Z]{2}\d+[A-Z]\d*)', html)
            if patent_ids:
                lines = [f"Found {len(patent_ids[:max_results])} patents (titles unavailable from search):"]
                for i, pid in enumerate(patent_ids[:max_results], 1):
                    lines.append(f"{i}. Patent {pid} — https://patents.google.com/patent/{pid}")
                return "\n".join(lines)
            return f"No patents found for: {query}"

        lines = [f"Google Patents results for '{query}':\n"]
        for i, (url, title) in enumerate(matches[:max_results], 1):
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_url = urllib.parse.unquote(url)
            # Extract patent ID from URL
            pid_match = re.search(r'/patent/([A-Z]{2}\d+[A-Z]?\d*)', clean_url)
            pid = pid_match.group(1) if pid_match else ""
            lines.append(f"{i}. {clean_title}")
            if pid:
                lines.append(f"   Patent: {pid}")
            lines.append(f"   URL: {clean_url}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error searching patents: {e}"
