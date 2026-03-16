import os
import googlemaps


def search_places(query: str, location: str = '', radius: int = 5000) -> str:
    """
    Search for places using Google Maps API.

    Args:
        query: Search query (e.g., "restaurants", "gas stations")
        location: Location to search near (optional)
        radius: Search radius in meters (default 5000)

    Returns:
        Formatted string with up to 10 place results
    """
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable not set"

    try:
        client = googlemaps.Client(key=api_key)
        response = client.places(query=query, location=location, radius=radius)

        results = []
        for place in response.get('results', [])[:10]:  # Limit to 10 results
            name = place.get('name', 'N/A')
            address = place.get('formatted_address', 'N/A')
            rating = place.get('rating', 'N/A')
            total_ratings = place.get('user_ratings_total', 'N/A')
            place_id = place.get('place_id', 'N/A')
            types = ', '.join(place.get('types', []))
            business_status = place.get('business_status', 'N/A')

            result = (
                f"Name: {name}\n"
                f"Address: {address}\n"
                f"Rating: {rating} ({total_ratings} ratings)\n"
                f"Place ID: {place_id}\n"
                f"Types: {types}\n"
                f"Business Status: {business_status}\n"
                f"---\n"
            )
            results.append(result)

        if not results:
            return "No places found for the given query."

        return ''.join(results)

    except Exception as e:
        return f"Error occurred while searching for places: {str(e)}"


def place_details(place_id: str) -> str:
    """
    Get detailed information about a specific place using its place_id.

    Args:
        place_id: Google Maps place ID

    Returns:
        Formatted string with place details
    """
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable not set"

    try:
        client = googlemaps.Client(key=api_key)
        response = client.place(place_id=place_id)

        result = response.get('result', {})

        name = result.get('name', 'N/A')
        formatted_address = result.get('formatted_address', 'N/A')
        phone = result.get('formatted_phone_number', 'N/A')
        website = result.get('website', 'N/A')
        rating = result.get('rating', 'N/A')

        # Get first 3 reviews
        reviews = result.get('reviews', [])[:3]
        review_texts = []
        for review in reviews:
            author = review.get('author_name', 'Anonymous')
            rating = review.get('rating', 'N/A')
            text = review.get('text', '')[:200] + "..." if len(review.get('text', '')) > 200 else review.get('text', '')
            review_texts.append(f"Reviewer: {author}, Rating: {rating}, Review: {text}")

        opening_hours = result.get('opening_hours', {}).get('weekday_text', 'N/A')
        price_level = result.get('price_level', 'N/A')

        details = (
            f"Name: {name}\n"
            f"Address: {formatted_address}\n"
            f"Phone: {phone}\n"
            f"Website: {website}\n"
            f"Rating: {rating}\n"
            f"Opening Hours: {opening_hours}\n"
            f"Price Level: {price_level}\n"
            f"Reviews:\n"
        )

        if review_texts:
            for i, review in enumerate(review_texts, 1):
                details += f"  {i}. {review}\n"
        else:
            details += "  No reviews available\n"

        return details

    except Exception as e:
        return f"Error occurred while getting place details: {str(e)}"