import urllib.request
import json
from typing import Dict, Any, Optional


def search_books(query: str, max_results: int = 5) -> str:
    """
    Search for books using the Google Books API.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 5)

    Returns:
        Formatted string with search results
    """
    try:
        # Encode the query for URL
        import urllib.parse
        encoded_query = urllib.parse.quote(query)

        # Construct the API URL
        url = f"https://www.googleapis.com/books/v1/volumes?q={encoded_query}&maxResults={max_results}"

        # Make the HTTP request
        with urllib.request.urlopen(url) as response:
            data = response.read()
            books_data = json.loads(data)

        # Check if any items were returned
        if 'items' not in books_data or len(books_data['items']) == 0:
            return "No books found for the given query."

        # Format the results
        result_parts = []
        for idx, item in enumerate(books_data['items'], start=1):
            volume_info = item.get('volumeInfo', {})

            title = volume_info.get('title', 'N/A')
            authors = ', '.join(volume_info.get('authors', ['N/A']))
            published_date = volume_info.get('publishedDate', 'N/A')

            description = volume_info.get('description', '')
            if description:
                # Truncate description to first 200 characters
                description = description[:200] + '...' if len(description) > 200 else description
            else:
                description = 'N/A'

            page_count = volume_info.get('pageCount', 'N/A')
            categories = ', '.join(volume_info.get('categories', ['N/A']))
            average_rating = volume_info.get('averageRating', 'N/A')
            preview_link = volume_info.get('previewLink', 'N/A')
            info_link = volume_info.get('infoLink', 'N/A')

            # Format the book info
            book_info = (
                f"{idx}. {title}\n"
                f"   Author(s): {authors}\n"
                f"   Published: {published_date}\n"
                f"   Description: {description}\n"
                f"   Pages: {page_count}\n"
                f"   Category: {categories}\n"
                f"   Rating: {average_rating}\n"
                f"   Preview: {preview_link}\n"
                f"   Info: {info_link}\n"
            )
            result_parts.append(book_info)

        return '\n'.join(result_parts)

    except urllib.error.HTTPError as e:
        return f"HTTP Error occurred while searching for books: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"URL Error occurred while searching for books: {e.reason}"
    except json.JSONDecodeError as e:
        return f"Error decoding JSON response: {e}"
    except Exception as e:
        return f"An unexpected error occurred while searching for books: {str(e)}"


if __name__ == "__main__":
    # Example usage
    print(search_books("python programming"))