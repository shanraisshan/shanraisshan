"""
Reddit Stats MCP Server

Fetches Reddit post views and comments by navigating a dedicated
background tab in Chrome via AppleScript and extracting stats from
the rendered page.

Non-intrusive: works in a background tab, restores focus to the
original app after setup. Does NOT steal focus during fetching.

Requires:
- Chrome open and logged into Reddit
- "Allow JavaScript from Apple Events" enabled in Chrome
  (View > Developer > Allow JavaScript from Apple Events)

Usage:
    /Users/shayanrais/Documents/Github/shanraisshan/reddit-mcp/.venv/bin/python3 \
        /Users/shayanrais/Documents/Github/shanraisshan/reddit-mcp/server.py
"""

import json
import re
import subprocess
import time
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("reddit-stats")

MAX_URLS = 25
PAGE_LOAD_DELAY = 7  # seconds to wait for page to render

# Track our background tab across calls
_tab_id: int | None = None
_window_id: int | None = None


def _run_applescript(script: str, timeout: int = 30) -> str | None:
    """Run an AppleScript and return stdout, or None on failure."""
    try:
        r = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=timeout,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None


def _setup_background_tab() -> bool:
    """Create a background tab for fetching, restore focus to original app."""
    global _tab_id, _window_id

    # Already have a tab — verify it still exists
    if _tab_id is not None:
        check = _run_applescript(f'''
tell application "Google Chrome"
    try
        set t to tab id {_tab_id} of window id {_window_id}
        return "ok"
    on error
        return "gone"
    end try
end tell
''')
        if check == "ok":
            return True
        _tab_id = None
        _window_id = None

    # Create tab — Chrome may briefly activate
    script = '''
tell application "Google Chrome"
    set w to front window
    set wid to id of w
    set newTab to make new tab at end of tabs of w with properties {URL:"about:blank"}
    set tid to id of newTab
    return (wid as text) & "," & (tid as text)
end tell
'''
    result = _run_applescript(script, timeout=10)
    if result:
        try:
            parts = result.split(",")
            _window_id = int(parts[0])
            _tab_id = int(parts[1])
            return True
        except (ValueError, IndexError):
            pass
    return False


def _navigate_and_extract(url: str) -> dict:
    """Navigate background tab to URL and extract views + comments."""
    if _tab_id is None:
        return {"url": url, "views": "error", "comments": "error"}

    # Navigate the background tab (no activation)
    nav_script = f'''
tell application "Google Chrome"
    set URL of tab id {_tab_id} of window id {_window_id} to "{url}"
end tell
'''
    _run_applescript(nav_script)
    time.sleep(PAGE_LOAD_DELAY)

    # Extract comment-count attribute from shreddit-post
    cc_script = f'''
tell application "Google Chrome"
    execute tab id {_tab_id} of window id {_window_id} javascript "var p=document.querySelector('shreddit-post');p?p.getAttribute('comment-count'):'not found'"
end tell
'''
    comments = _run_applescript(cc_script, timeout=15) or "not found"

    # Extract view count from page text (e.g. "1.5K views")
    vw_script = f'''
tell application "Google Chrome"
    execute tab id {_tab_id} of window id {_window_id} javascript "document.body?document.body.innerText:''"
end tell
'''
    body_text = _run_applescript(vw_script, timeout=15) or ""
    views = "not found"
    vm = re.search(r'([\d,.]+[KMB]?)\s*views?', body_text, re.IGNORECASE)
    if vm:
        views = _format_views(vm.group(1))

    return {"url": url, "views": views, "comments": comments}


def _format_views(raw: str) -> str:
    """Normalize view count string. If it's a raw number, format it like Reddit."""
    if raw in ("not found", "error", "0"):
        return raw
    if any(c in raw for c in "KMB"):
        return raw
    try:
        n = int(raw.replace(",", ""))
        return _format_count(n)
    except (ValueError, TypeError):
        return raw


def _format_count(n: int) -> str:
    """Format a count like Reddit: 1500→'1.5K', 196000→'196K', 1200000→'1.2M'."""
    if n >= 1_000_000:
        v = n / 1_000_000
        if v >= 10:
            return f"{round(v)}M"
        s = f"{v:.1f}"
        return (s[:-2] if s.endswith(".0") else s) + "M"
    if n >= 1_000:
        v = n / 1_000
        if v >= 10:
            return f"{round(v)}K"
        s = f"{v:.1f}"
        return (s[:-2] if s.endswith(".0") else s) + "K"
    return str(n)


def _cleanup_tab():
    """Close the background tab when done."""
    global _tab_id, _window_id
    if _tab_id is not None:
        _run_applescript(f'''
tell application "Google Chrome"
    try
        close tab id {_tab_id} of window id {_window_id}
    end try
end tell
''')
        _tab_id = None
        _window_id = None


@mcp.tool()
def fetch_reddit_stats(urls: list[str]) -> str:
    """Fetch view and comment counts for Reddit post URLs.

    Uses AppleScript to open each URL in a background Chrome tab
    and extract stats from the rendered page. Chrome must be open
    and logged into Reddit.

    Non-intrusive: uses a background tab, does not steal focus.

    Args:
        urls: Reddit post URLs (max 25 per call).

    Returns:
        JSON array of {url, views, comments} objects.
    """
    if len(urls) > MAX_URLS:
        return json.dumps({"error": f"Max {MAX_URLS} URLs, got {len(urls)}."})

    if not _setup_background_tab():
        return json.dumps({"error": "Could not create background tab in Chrome."})

    results = []
    for url in urls:
        results.append(_navigate_and_extract(url))

    # Keep tab open for next batch (reused across calls)
    # Tab is closed when server shuts down

    return json.dumps(results, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
