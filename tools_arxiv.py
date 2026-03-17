import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional


def search_arxiv(query: str, max_results: int = 5) -> str:
    """
    Search the arXiv API for papers matching the query.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 5)

    Returns:
        Formatted string with search results
    """
    try:
        # URL encode the query
        encoded_query = urllib.parse.quote(query)

        # Construct the API URL
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"

        # Make the HTTP request
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')

        # Parse the XML
        root = ET.fromstring(data)

        # Define namespace
        ns = "{http://www.w3.org/2005/Atom}"

        # Extract entries
        entries = root.findall(f"{ns}entry")

        if not entries:
            return "No results found."

        # Format results
        result_parts = []
        for i, entry in enumerate(entries, 1):
            # Extract title
            title_elem = entry.find(f"{ns}title")
            title = title_elem.text.strip() if title_elem is not None else "No title"

            # Extract authors
            author_elems = entry.findall(f"{ns}author/{ns}name")
            authors = [author.text.strip() for author in author_elems if author.text]
            authors_str = ", ".join(authors) if authors else "Unknown authors"

            # Extract published date
            published_elem = entry.find(f"{ns}published")
            published = published_elem.text.strip() if published_elem is not None else "Unknown date"

            # Extract summary (first 300 chars)
            summary_elem = entry.find(f"{ns}summary")
            summary = summary_elem.text.strip() if summary_elem is not None else "No summary"
            summary_preview = summary[:300] + "..." if len(summary) > 300 else summary

            # Extract arxiv ID
            id_elem = entry.find(f"{ns}id")
            arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None else "Unknown ID"

            # Extract PDF link
            pdf_link = ""
            link_elems = entry.findall(f"{ns}link")
            for link in link_elems:
                if link.get('title') == 'pdf':
                    pdf_link = link.get('href', '')
                    break

            # Format entry
            entry_str = (
                f"{i}. **Title**: {title}\n"
                f"   **Authors**: {authors_str}\n"
                f"   **Published**: {published}\n"
                f"   **Abstract Preview**: {summary_preview}\n"
                f"   **arXiv ID**: {arxiv_id}\n"
                f"   **PDF Link**: {pdf_link}\n"
            )
            result_parts.append(entry_str)

        return "\n".join(result_parts)

    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"URL Error: {e.reason}"
    except ET.ParseError as e:
        return f"XML Parse Error: {e}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def get_paper(arxiv_id: str) -> str:
    """
    Get detailed information about a specific paper by arXiv ID.

    Args:
        arxiv_id: The arXiv ID of the paper

    Returns:
        Formatted string with paper details
    """
    try:
        # Construct the API URL
        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"

        # Make the HTTP request
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')

        # Parse the XML
        root = ET.fromstring(data)

        # Define namespace
        ns = "{http://www.w3.org/2005/Atom}"

        # Extract the entry
        entries = root.findall(f"{ns}entry")

        if not entries:
            return f"No paper found with arXiv ID: {arxiv_id}"

        entry = entries[0]

        # Extract title
        title_elem = entry.find(f"{ns}title")
        title = title_elem.text.strip() if title_elem is not None else "No title"

        # Extract authors
        author_elems = entry.findall(f"{ns}author/{ns}name")
        authors = [author.text.strip() for author in author_elems if author.text]
        authors_str = ", ".join(authors) if authors else "Unknown authors"

        # Extract published date
        published_elem = entry.find(f"{ns}published")
        published = published_elem.text.strip() if published_elem is not None else "Unknown date"

        # Extract updated date
        updated_elem = entry.find(f"{ns}updated")
        updated = updated_elem.text.strip() if updated_elem is not None else published  # Fallback to published if no updated

        # Extract summary (full abstract)
        summary_elem = entry.find(f"{ns}summary")
        full_abstract = summary_elem.text.strip() if summary_elem is not None else "No abstract"

        # Extract categories
        category_elems = entry.findall(f"{ns}category")
        categories = [cat.get('term', '') for cat in category_elems]
        categories_str = ", ".join(categories) if categories else "No categories"

        # Extract comments
        comment_elem = entry.find(f"{ns}comment")
        comments = comment_elem.text.strip() if comment_elem is not None else "No comments"

        # Extract DOI if available
        doi = "Not available"
        link_elems = entry.findall(f"{ns}link")
        for link in link_elems:
            if 'doi.org' in link.get('href', ''):
                doi = link.get('href', 'Not available')
                break

        # Extract arxiv ID again from the id element
        id_elem = entry.find(f"{ns}id")
        full_arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None else arxiv_id

        # Extract PDF link
        pdf_link = ""
        for link in link_elems:
            if link.get('title') == 'pdf':
                pdf_link = link.get('href', '')
                break

        # Format the detailed view
        result = (
            f"**Title**: {title}\n"
            f"**arXiv ID**: {full_arxiv_id}\n"
            f"**Authors**: {authors_str}\n"
            f"**Published**: {published}\n"
            f"**Updated**: {updated}\n"
            f"**Categories**: {categories_str}\n"
            f"**DOI**: {doi}\n"
            f"**Comments**: {comments}\n"
            f"**PDF Link**: {pdf_link}\n"
            f"\n**Abstract**:\n{full_abstract}\n"
        )

        return result

    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"URL Error: {e.reason}"
    except ET.ParseError as e:
        return f"XML Parse Error: {e}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"