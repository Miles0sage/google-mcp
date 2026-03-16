def search_youtube(query: str, max_results: int = 10) -> str:
    """
    Search YouTube for videos using the provided query.

    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return (default: 10)

    Returns:
        str: Formatted list of video information
    """
    try:
        import scrapetube
    except ImportError:
        return "Error: scrapetube library is not installed. Please install it with 'pip install scrapetube'"

    try:
        videos = list(scrapetube.get_search(query, limit=max_results))

        result = []
        for i, video in enumerate(videos, 1):
            video_id = video.get('videoId', 'N/A')
            title = 'N/A'
            if 'title' in video and 'runs' in video['title']:
                title = video['title']['runs'][0].get('text', 'N/A')

            view_count = video.get('viewCountText', {}).get('simpleText', 'N/A')
            length = video.get('lengthText', {}).get('simpleText', 'N/A')
            published_time = video.get('publishedTimeText', {}).get('simpleText', 'N/A')

            # Extract channel name
            channel_name = 'N/A'
            if 'ownerText' in video and 'runs' in video['ownerText']:
                channel_name = video['ownerText']['runs'][0].get('text', 'N/A')

            video_url = f"https://youtube.com/watch?v={video_id}"

            result.append(f"{i}. {title}\n   Channel: {channel_name}\n   Views: {view_count}\n   Duration: {length}\n   Published: {published_time}\n   URL: {video_url}\n")

        return "\n".join(result)

    except Exception as e:
        return f"Error occurred while searching YouTube: {str(e)}"


def channel_videos(channel_url: str, max_results: int = 10) -> str:
    """
    Get videos from a specific YouTube channel.

    Args:
        channel_url (str): The URL of the YouTube channel
        max_results (int): Maximum number of results to return (default: 10)

    Returns:
        str: Formatted list of video information
    """
    try:
        import scrapetube
    except ImportError:
        return "Error: scrapetube library is not installed. Please install it with 'pip install scrapetube'"

    try:
        videos = list(scrapetube.get_channel(channel_url=channel_url, limit=max_results))

        result = []
        for i, video in enumerate(videos, 1):
            video_id = video.get('videoId', 'N/A')
            title = 'N/A'
            if 'title' in video and 'runs' in video['title']:
                title = video['title']['runs'][0].get('text', 'N/A')

            view_count = video.get('viewCountText', {}).get('simpleText', 'N/A')
            length = video.get('lengthText', {}).get('simpleText', 'N/A')
            published_time = video.get('publishedTimeText', {}).get('simpleText', 'N/A')

            # Extract channel name
            channel_name = 'N/A'
            if 'ownerText' in video and 'runs' in video['ownerText']:
                channel_name = video['ownerText']['runs'][0].get('text', 'N/A')

            video_url = f"https://youtube.com/watch?v={video_id}"

            result.append(f"{i}. {title}\n   Channel: {channel_name}\n   Views: {view_count}\n   Duration: {length}\n   Published: {published_time}\n   URL: {video_url}\n")

        return "\n".join(result)

    except Exception as e:
        return f"Error occurred while fetching channel videos: {str(e)}"