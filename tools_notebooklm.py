"""NotebookLM automation via notebooklm-py library (no browser needed)."""

import asyncio
from typing import Optional


async def _get_client():
    """Get authenticated NotebookLMClient from saved storage."""
    from notebooklm import NotebookLMClient
    client = await NotebookLMClient.from_storage()
    return client


def _run_async(coro_fn):
    """Run async function, handling both standalone and nested event loop contexts."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Already inside an event loop (MCP server context) — use nest_asyncio
        try:
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(coro_fn())
        except ImportError:
            # Fallback: create new thread with its own event loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro_fn())
                return future.result(timeout=60)
    else:
        return asyncio.run(coro_fn())


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
        return _run_async(_run)
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
        return _run_async(_run)
    except Exception as e:
        return f"Error creating notebook: {e}"


def add_source(notebook_id: str, url: str) -> str:
    """Add a URL source to an existing notebook."""
    async def _run():
        async with await _get_client() as client:
            source = await client.sources.add_url(notebook_id, url)
            return f"Source added: {source.title} (status: {source.status})"
    try:
        return _run_async(_run)
    except Exception as e:
        return f"Error adding source: {e}"


def add_text_source(notebook_id: str, title: str, text: str) -> str:
    """Add a text/paste source to a notebook."""
    async def _run():
        async with await _get_client() as client:
            source = await client.sources.add_text(notebook_id, title=title, text=text)
            return f"Text source added: {source.title} (status: {source.status})"
    try:
        return _run_async(_run)
    except Exception as e:
        return f"Error adding text source: {e}"


def add_youtube_source(notebook_id: str, youtube_url: str) -> str:
    """Add a YouTube video as a source to a notebook."""
    async def _run():
        async with await _get_client() as client:
            source = await client.sources.add_youtube(notebook_id, youtube_url)
            return f"YouTube source added: {source.title} (status: {source.status})"
    try:
        return _run_async(_run)
    except Exception as e:
        return f"Error adding YouTube source: {e}"


def generate_podcast(notebook_id: str) -> str:
    """Generate an Audio Overview (podcast) for a notebook."""
    async def _run():
        client = await _get_client()
        await client.__aenter__()
        try:
            gen = await client.artifacts.generate_audio(notebook_id)
            return f"Podcast generation started (task: {gen.task_id}, status: {gen.status})\nNote: Generation takes 2-5 minutes. Check notebooklm.google.com for the audio player."
        finally:
            await client.__aexit__(None, None, None)
    try:
        return _run_async(_run)
    except Exception as e:
        return f"Error generating podcast: {e}"


def ask_notebook(notebook_id: str, question: str) -> str:
    """Ask a question to a notebook's sources."""
    async def _run():
        async with await _get_client() as client:
            result = await client.chat.ask(notebook_id, question)
            refs = len(result.references) if result.references else 0
            return f"Answer: {result.answer}\n\nReferences: {refs} citations"
    try:
        return _run_async(_run)
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
        return _run_async(_run)
    except Exception as e:
        return f"Error listing sources: {e}"
