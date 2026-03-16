"""NotebookLM automation via Playwright browser automation."""

import asyncio
import json
import os

STORAGE_STATE = os.getenv(
    "NOTEBOOKLM_STORAGE_STATE",
    os.path.expanduser("~/.notebooklm/storage_state.json"),
)


async def _get_browser():
    """Launch Playwright browser with NotebookLM auth cookies."""
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
    context = await browser.new_context(storage_state=STORAGE_STATE)
    return pw, browser, context


def create_notebook(title: str, source_urls: list[str]) -> str:
    """
    Create a NotebookLM notebook and add source URLs.

    Args:
        title: Notebook title
        source_urls: List of URLs to add as sources

    Returns:
        Status message with notebook URL
    """
    try:
        return asyncio.run(_create_notebook_async(title, source_urls))
    except Exception as e:
        return f"Error creating notebook: {e}"


async def _create_notebook_async(title: str, source_urls: list[str]) -> str:
    if not os.path.exists(STORAGE_STATE):
        return (
            f"NotebookLM storage_state.json not found at {STORAGE_STATE}. "
            "Login to notebooklm.google.com in Playwright first and save cookies."
        )

    pw, browser, context = await _get_browser()
    try:
        page = await context.new_page()
        await page.goto("https://notebooklm.google.com/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Click "New notebook" or "+" button
        new_btn = page.locator('button:has-text("New"), button:has-text("Create"), [aria-label*="new"]').first
        await new_btn.click()
        await page.wait_for_timeout(2000)

        added = 0
        for url in source_urls[:20]:  # Max 20 sources
            try:
                # Click add source
                add_btn = page.locator('button:has-text("Add source"), button:has-text("Add"), [aria-label*="source"]').first
                await add_btn.click()
                await page.wait_for_timeout(1000)

                # Look for URL/website option
                url_option = page.locator('text=Website, text=URL, text=Link').first
                await url_option.click()
                await page.wait_for_timeout(500)

                # Paste URL
                url_input = page.locator('input[type="url"], input[type="text"], textarea').first
                await url_input.fill(url)
                await page.wait_for_timeout(500)

                # Submit
                submit_btn = page.locator('button:has-text("Insert"), button:has-text("Add"), button:has-text("Submit")').first
                await submit_btn.click()
                await page.wait_for_timeout(3000)
                added += 1
            except Exception:
                continue

        notebook_url = page.url
        return f"Notebook created: {notebook_url}\nSources added: {added}/{len(source_urls)}"
    finally:
        await browser.close()
        await pw.stop()


def generate_podcast(notebook_url: str) -> str:
    """
    Trigger Audio Overview (podcast) generation for a NotebookLM notebook.

    Args:
        notebook_url: URL of the NotebookLM notebook

    Returns:
        Status of podcast generation
    """
    try:
        return asyncio.run(_generate_podcast_async(notebook_url))
    except Exception as e:
        return f"Error generating podcast: {e}"


async def _generate_podcast_async(notebook_url: str) -> str:
    if not os.path.exists(STORAGE_STATE):
        return f"NotebookLM storage_state.json not found at {STORAGE_STATE}."

    pw, browser, context = await _get_browser()
    try:
        page = await context.new_page()
        await page.goto(notebook_url, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Find and click "Audio Overview" or "Generate" button
        audio_btn = page.locator(
            'button:has-text("Audio Overview"), '
            'button:has-text("Generate audio"), '
            'button:has-text("Notebook guide"), '
            '[aria-label*="audio"], [aria-label*="podcast"]'
        ).first
        await audio_btn.click()
        await page.wait_for_timeout(2000)

        # Click generate/create
        gen_btn = page.locator(
            'button:has-text("Generate"), button:has-text("Create")'
        ).first
        await gen_btn.click()
        await page.wait_for_timeout(5000)

        return f"Podcast generation triggered for: {notebook_url}\nNote: Generation takes 2-5 minutes. Check the notebook for the audio player."
    finally:
        await browser.close()
        await pw.stop()
