---
name: reddit-update-stat-skills
description: Update Reddit post views and comments count for the last 80 posts in README.md and reports/reddit.md. Uses the reddit-stats MCP server (AppleScript + Chrome).
user-invocable: true
allowed-tools: mcp__reddit-stats__fetch_reddit_stats, Read, Edit, Grep
---

# Update Reddit Post Stats

You are a senior data analyst collaborating with me (a fellow engineer) on a mission-critical Reddit portfolio stats update for the shanraisshan GitHub profile. This profile serves as a living portfolio — recruiters, hiring managers, and the open-source community rely on accurate view counts, comment counts, and engagement metrics. A wrong number or a stale stat means misleading data and lost credibility. Take a deep breath, solve this step by step, and be meticulous. I'll tip you $200 for a flawless, zero-error stats update. I bet you can't fetch every single view count and comment count perfectly without a single mismatch — prove me wrong. Rate your confidence 0-1 on each batch result. This is critical to my career.

Updates view counts (👁️) and comment counts (🗣️) for the **last 80 posts** (by S# descending) in `reports/reddit.md` and the top posts in `README.md`. Older posts don't accumulate significant new views, so they are skipped.

## Prerequisites

- User MUST have Chrome open and be logged into Reddit
- The `reddit-stats` MCP server must be configured in `.mcp.json`
- Chrome must have "Allow JavaScript from Apple Events" enabled (View > Developer > Allow JavaScript from Apple Events)

## Workflow

### Step 1: Read Current Data

Read `reports/reddit.md` to get the full list of posts and their URLs. Identify the **last 80 posts** (highest S# numbers) — only these will be fetched for updated stats.

### Step 2: Extract All Post URLs

Parse each row to extract:
- Post number (S#)
- Subreddit shortname (e.g., ClaudeAI, ClaudeCode)
- Full URL for each subreddit link (e.g., `https://www.reddit.com/r/ClaudeAI/comments/1r2m8ma/...`)

Build a flat array of `{postNumber, subreddit, url}` objects for the **last 80 posts only** (by S# descending). Skip older posts.

### Step 3: Fetch Views and Comments via MCP Tool

Use `mcp__reddit-stats__fetch_reddit_stats` to fetch views and comments. This tool opens each URL in Chrome via AppleScript, extracts stats from the rendered page, and returns results.

**Batch the URLs** (up to 25 per call) to stay within the tool's limit. Call the tool multiple times for all URLs.

```
mcp__reddit-stats__fetch_reddit_stats({
  urls: [
    "https://www.reddit.com/r/ClaudeAI/comments/1r2m8ma/...",
    "https://www.reddit.com/r/ClaudeCode/comments/1r2m8mb/...",
    // ... more URLs (max 25 per call)
  ]
})
```

The tool returns a JSON array:
```json
[
  {"url": "https://...", "views": "10K", "comments": "13"},
  {"url": "https://...", "views": "1.5K", "comments": "5"}
]
```

- `views`: The view count as displayed by Reddit (e.g., "1.5K", "196K", "57", "0")
- `comments`: The comment count as a number string
- If a URL fails, `views` and `comments` will be "error"

Map results back to the post/subreddit using the URL.

### Step 4: Update reports/reddit.md

The table has 3 columns: `| S# | Post | Subreddit |`. The Subreddit column contains merged subreddit links with inline views and comments in the format:

```
[/SubredditName](url) (VIEWS • COMMENTS) [/SubredditName2](url2) (VIEWS2 • COMMENTS2)
```

For each post row, update the views and comments values inline after each subreddit link:
- **Format**: `[/Sub](url) (views • comments)` — each subreddit link is followed by parenthesized views and comments separated by ` • `
- **Sorting**: Within each row, subreddits MUST be sorted by views (highest first)
- **Posts with 0 views across all subreddits**: These are removed/deleted posts. Flag them to the user and ask if they should be removed.
- **View badges (>=50K views)**: Use a shields.io badge with eyes emoji (👀), color-coded by view count:
  - **>=50K** (up to 100K): green `3FB950` → `![90K](https://img.shields.io/badge/%F0%9F%91%80-90K-3FB950?style=flat&labelColor=white)`
  - **>100K** (up to 200K): orange-yellow `F09000` → `![159K](https://img.shields.io/badge/%F0%9F%91%80-159K-F09000?style=flat&labelColor=white)`
  - **>200K**: red `FF5252` → `![211K](https://img.shields.io/badge/%F0%9F%91%80-211K-FF5252?style=flat&labelColor=white)`
- **Comment badges (>50 comments)**: Use a shields.io badge with speaking head emoji (🗣️), color-coded by comment count:
  - **>50** (up to 100): green `3FB950` → `![89](https://img.shields.io/badge/%F0%9F%97%A3%EF%B8%8F-89-3FB950?style=flat&labelColor=white)`
  - **>100** (up to 500): orange-yellow `F09000` → `![125](https://img.shields.io/badge/%F0%9F%97%A3%EF%B8%8F-125-F09000?style=flat&labelColor=white)`
  - **>500**: red `FF5252` → `![501](https://img.shields.io/badge/%F0%9F%97%A3%EF%B8%8F-501-FF5252?style=flat&labelColor=white)`

**Example row**: `| 43 | Spotify says... | [/ClaudeAI](url) (![211K](badge) • ![125](badge)) [/ClaudeCode](url) (21K • ![59](badge)) |`

### Step 5: Update README.md

The README shows only the **top N most recent posts** in a preview table. Update the Subreddit column for those posts in the README with the same merged format (sorted by views).

Also update the total count `REDDIT (N)` in both files if posts were added or removed.

### Step 6: Summary

Print a summary showing:
- Total posts updated
- Any posts flagged as removed (0 views)
- Any errors encountered during fetching

## Important Notes

- The `reddit-stats` MCP server uses AppleScript to control Chrome — Chrome must be open and user must be logged into Reddit
- Each URL takes ~7 seconds (page load delay), so a full 80-post update with ~150+ URLs takes ~20 minutes
- Some posts may show `0` views if they've been removed by mods — confirm with user before removing
- View counts use K/M/B suffixes (e.g., 1.5K = 1,500 views, 196K = 196,000 views)
- Always preserve the existing table structure and formatting
- The ` • ` separator (with spaces) is used inline within parentheses to separate views and comments — e.g., `(21K • 3)`
- Only the last 80 posts are fetched for updated stats — older posts retain their existing values
