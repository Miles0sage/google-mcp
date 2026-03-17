"""NotebookLM automation via notebooklm-py library (no browser needed)."""

import asyncio
from typing import Optional


async def _get_client():
    """Get authenticated NotebookLMClient from saved storage."""
    from notebooklm import NotebookLMClient
    return NotebookLMClient.from_storage()


def list_notebooks() -> str:
    """List all NotebookLM notebooks."""
    async def _run():
        async with await _get_client() as client:
            notebooks = await client.notebooks.list()
            if not notebooks:
                return "No notebooks found."
            lines = []
            for i, nb in enumerate(notebooks, 1):
                lines.append(f"{i}. {nb.title} (ID: {nb.id})")
            return f"Notebooks ({len(notebooks)}):\n" + "\n".join(lines)
    try:
        return asyncio.run(_run())
    except Exception as e:
        return f"Error listing notebooks: {e}"


def create_notebook(title: str, source_urls: list[str]) -> str:
    """Create a NotebookLM notebook and add source URLs."""
    async def _run():
        async with await _get_client() as client:
            nb = await client.notebooks.create(title=title)
            added = 0
            errors = []
            for url in source_urls[:50]:
                try:
                    await client.sources.add_url(nb.id, url)
                    added += 1
                except Exception as e:
                    errors.append(f"{url}: {e}")
            result = f"Notebook created: {nb.title} (ID: {nb.id})\nSources added: {added}/{len(source_urls)}"
            if errors:
                result += f"\nErrors:\n" + "\n".join(errors[:5])
            return result
    try:
        return asyncio.run(_run())
    except Exception as e:
        return f"Error creating notebook: {e}"


def add_source(notebook_id: str, url: str) -> str:
    """Add a URL source to an existing notebook."""
    async def _run():
        async with await _get_client() as client:
            source = await client.sources.add_url(notebook_id, url)
            return f"Source added: {source.title} (status: {source.status})"
    try:
        return asyncio.run(_run())
    except Exception as e:
        return f"Error adding source: {e}"


def add_text_source(notebook_id: str, title: str, text: str) -> str:
    """Add a text/paste source to a notebook."""
    async def _run():
        async with await _get_client() as client:
            source = await client.sources.add_text(notebook_id, title=title, text=text)
            return f"Text source added: {source.title} (status: {source.status})"
    try:
        return asyncio.run(_run())
    except Exception as e:
        return f"Error adding text source: {e}"


def add_youtube_source(notebook_id: str, youtube_url: str) -> str:
    """Add a YouTube video as a source to a notebook."""
    async def _run():
        async with await _get_client() as client:
            source = await client.sources.add_youtube(notebook_id, youtube_url)
            return f"YouTube source added: {source.title} (status: {source.status})"
    try:
        return asyncio.run(_run())
    except Exception as e:
        return f"Error adding YouTube source: {e}"


def generate_podcast(notebook_id: str) -> str:
    """Generate an Audio Overview (podcast) for a notebook."""
    async def _run():
        from notebooklm import ArtifactType
        async with await _get_client() as client:
            artifact = await client.artifacts.generate(notebook_id, ArtifactType.AUDIO)
            return f"Podcast generation started (ID: {artifact.id}, status: {artifact.status})\nNote: Generation takes 2-5 minutes."
    try:
        return asyncio.run(_run())
    except Exception as e:
        return f"Error generating podcast: {e}"


def ask_notebook(notebook_id: str, question: str) -> str:
    """Ask a question to a notebook's sources."""
    async def _run():
        async with await _get_client() as client:
            result = await client.chat.ask(notebook_id, question)
            return f"Answer: {result.text}\n\nReferences: {len(result.references) if hasattr(result, 'references') else 'N/A'}"
    try:
        return asyncio.run(_run())
    except Exception as e:
        return f"Error asking notebook: {e}"


def notebook_sources(notebook_id: str) -> str:
    """List all sources in a notebook."""
    async def _run():
        async with await _get_client() as client:
            sources = await client.sources.list(notebook_id)
            if not sources:
                return "No sources in this notebook."
            lines = []
            for i, s in enumerate(sources, 1):
                lines.append(f"{i}. {s.title} ({s.type}, status: {s.status})")
            return f"Sources ({len(sources)}):\n" + "\n".join(lines)
    try:
        return asyncio.run(_run())
    except Exception as e:
        return f"Error listing sources: {e}"
