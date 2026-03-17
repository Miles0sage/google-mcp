import urllib.request
import urllib.parse
import re
import ssl


def extract_webpage(url: str, max_chars: int = 5000) -> str:
    """
    Extract main text content from a webpage.

    Args:
        url: The URL to extract content from
        max_chars: Maximum number of characters to return (default 5000)

    Returns:
        Formatted string with title, URL, and content
    """
    # Set up the request with a browser-like User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    request = urllib.request.Request(url, headers=headers)

    # Create an SSL context that allows unverified connections (to handle SSL issues)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        # Make the request with a timeout of 10 seconds
        response = urllib.request.urlopen(request, timeout=10, context=ssl_context)
        html_bytes = response.read()

        # Decode the content
        try:
            html = html_bytes.decode('utf-8')
        except UnicodeDecodeError:
            html = html_bytes.decode('latin-1')

        # Extract title from the HTML
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        extracted_title = title_match.group(1).strip() if title_match else "No Title Found"

        # Remove script and style tags and their content
        cleaned_html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove all HTML tags
        text_only = re.sub(r'<[^>]+>', ' ', cleaned_html)

        # Collapse whitespace and clean up
        text = re.sub(r'\s+', ' ', text_only).strip()

        # Truncate to max_chars
        if len(text) > max_chars:
            text = text[:max_chars].rstrip() + "..."

        # Prepare the return string
        result = f'Title: {extracted_title}\nURL: {url}\nContent ({len(text)} chars):\n{text}'
        return result

    except urllib.error.HTTPError as e:
        if e.code == 403:
            return f'Access forbidden (403) for URL: {url}'
        else:
            return f'HTTP Error {e.code} for URL: {url}'
    except urllib.error.URLError as e:
        return f'URL Error for {url}: {e.reason}'
    except ssl.SSLError as e:
        return f'SSL Error for {url}: {str(e)}'
    except Exception as e:
        return f'Unexpected error for {url}: {str(e)}'


if __name__ == "__main__":
    # Example usage:
    # result = extract_webpage("https://www.example.com")
    # print(result)
    pass