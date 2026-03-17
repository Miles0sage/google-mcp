import urllib.request
import urllib.parse
import json
from typing import Optional


def translate_text(text: str, target_language: str = 'en', source_language: str = 'auto') -> str:
    """
    Translate text using the free Google Translate API.

    Args:
        text: The text to translate
        target_language: Target language code (default: 'en')
        source_language: Source language code (default: 'auto' for auto-detection)

    Returns:
        Formatted string with translation and language information
    """
    try:
        # URL encode the text
        encoded_text = urllib.parse.quote(text)

        # Construct the API URL
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_language}&tl={target_language}&dt=t&q={encoded_text}"

        # Make the request
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        response = urllib.request.urlopen(request)
        response_data = response.read().decode('utf-8')

        # Parse the JSON response
        parsed_response = json.loads(response_data)

        # Extract the translated text from the nested array structure
        translated_text = parsed_response[0][0][0]

        # If source language is 'auto', detect the language from response[2]
        detected_source = parsed_response[2] if source_language == 'auto' else source_language

        return f'Translated ({detected_source} → {target_language}): {translated_text}'

    except urllib.error.HTTPError as e:
        return f'HTTP Error {e.code}: Could not translate text ({e.reason})'

    except urllib.error.URLError as e:
        return f'URL Error: Could not connect to translation service ({e.reason})'

    except (IndexError, KeyError, TypeError):
        return 'Error: Could not parse translation response - invalid response format'

    except Exception as e:
        return f'Unexpected error during translation: {str(e)}'


# Example usage
if __name__ == '__main__':
    # Test the function
    result = translate_text("Hello, world!", "es")
    print(result)

    result_auto = translate_text("Bonjour", "en", "auto")
    print(result_auto)