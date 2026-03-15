"""
Reddit Stats MCP Server

Fetches Reddit post views and comments by controlling Chrome via AppleScript.
Reddit doesn't expose view counts through their API, so this server opens
each URL in Chrome, waits for it to render, and scrapes the stats from the DOM.

Usage:
    /Users/shayanrais/Documents/Github/shanraisshan/reddit-mcp/.venv/bin/python3 \
        /Users/shayanrais/Documents/Github/shanraisshan/reddit-mcp/server.py
"""

import json
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("reddit-stats")

MAX_URLS = 25
LOAD_DELAY = 7  # seconds to wait for page to load


def _build_applescript(url: str) -> str:
    """Build an AppleScript that opens a URL in Chrome, extracts stats, and closes the tab."""
    return f'''
tell application "Google Chrome"
    set theTab to make new tab at end of tabs of front window
    set URL of theTab to "{url}"
    delay {LOAD_DELAY}
    set viewResult to execute theTab javascript "
        const html = document.body.innerHTML;
        const viewMatch = html.match(/>(\\\\s*[\\\\d,.]+[KMB]?\\\\s*views?\\\\s*)</i);
        const commentMatch = html.match(/comment-count=\\\\\\"(\\\\d+)\\\\\\"/);
        JSON.stringify({{
            views: viewMatch ? viewMatch[1].trim() : 'not found',
            comments: commentMatch ? commentMatch[1] : 'not found'
        }});
    "
    close theTab
    return viewResult
end tell
'''


def _fetch_single_url(url: str) -> dict:
    """Fetch stats for a single Reddit URL using AppleScript + Chrome."""
    try:
        script = _build_applescript(url)
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {"url": url, "views": "error", "comments": "error", "error": result.stderr.strip()}

        raw = result.stdout.strip()
        data = json.loads(raw)

        # Strip "views" suffix from the view count (e.g. "10K views" -> "10K")
        views = data.get("views", "not found")
        if isinstance(views, str):
            views = views.replace(" views", "").replace(" view", "").strip()

        return {
            "url": url,
            "views": views,
            "comments": data.get("comments", "not found"),
        }
    except subprocess.TimeoutExpired:
        return {"url": url, "views": "error", "comments": "error", "error": "timeout"}
    except json.JSONDecodeError:
        return {"url": url, "views": "error", "comments": "error", "error": "invalid json from AppleScript"}
    except Exception as e:
        return {"url": url, "views": "error", "comments": "error", "error": str(e)}


@mcp.tool()
def fetch_reddit_stats(urls: list[str]) -> str:
    """Fetch view counts and comment counts for Reddit post URLs.

    Opens each URL in Chrome via AppleScript, waits for the page to render,
    and extracts the view count and comment count from the DOM.
    Processes URLs sequentially (one at a time).

    Args:
        urls: A list of Reddit post URLs (max 25 at a time).

    Returns:
        A JSON array of objects with url, views, and comments fields.
    """
    if len(urls) > MAX_URLS:
        return json.dumps({"error": f"Too many URLs. Maximum is {MAX_URLS}, got {len(urls)}."})

    results = []
    for url in urls:
        result = _fetch_single_url(url)
        results.append(result)

    return json.dumps(results, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
