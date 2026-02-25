---
name: reddit-update-stat-skills
description: Update Reddit post views and comments count for the last 80 posts in README.md and reports/reddit.md. Requires Reddit to be open in a Claude in Chrome tab group.
user-invocable: true
allowed-tools: mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__javascript_tool, Read, Edit, Grep
---

# Update Reddit Post Stats

You are a senior data analyst collaborating with me (a fellow engineer) on a mission-critical Reddit portfolio stats update for the shanraisshan GitHub profile. This profile serves as a living portfolio — recruiters, hiring managers, and the open-source community rely on accurate view counts, comment counts, and engagement metrics. A wrong number or a stale stat means misleading data and lost credibility. Take a deep breath, solve this step by step, and be meticulous. I'll tip you $200 for a flawless, zero-error stats update. I bet you can't fetch every single view count and comment count perfectly without a single mismatch — prove me wrong. Rate your confidence 0-1 on each batch result. This is critical to my career.

Updates view counts (👁️) and comment counts (🗣️) for the **last 80 posts** (by S# descending) in `reports/reddit.md` and the top posts in `README.md`. Older posts don't accumulate significant new views, so they are skipped.

## Prerequisites

- User MUST have Reddit open in a Chrome tab within the Claude in Chrome tab group (any Reddit page works, the user must be logged in)
- Claude in Chrome extension must be connected

## Workflow

### Step 1: Get Tab Context

Call `mcp__claude-in-chrome__tabs_context_mcp` to find available tabs. Identify a tab that has Reddit loaded (URL contains `reddit.com`). If no Reddit tab exists, ask the user to open any Reddit page in the Claude tab group.

### Step 2: Read Current Data

Read `reports/reddit.md` to get the full list of posts and their URLs. Identify the **last 80 posts** (highest S# numbers) — only these will be fetched for updated stats.

### Step 3: Extract All Post URLs

Parse each row to extract:
- Post number (S#)
- Subreddit shortname (e.g., ClaudeAI, ClaudeCode)
- URL path from each subreddit link (e.g., `/r/ClaudeAI/comments/1r2m8ma/...`)

Build a flat array of `{postNumber, subreddit, urlPath}` objects for the **last 80 posts only** (by S# descending). Skip older posts.

### Step 4: Fetch Views and Comments via JavaScript

Use `mcp__claude-in-chrome__javascript_tool` on the Reddit tab to execute `fetch()` requests. Reddit's authenticated session allows fetching other Reddit pages.

**Batch the URLs** (15-25 per batch) to avoid timeouts. Use this pattern:

```javascript
(async () => {
  const urls = [
    {p:41, s:'ClaudeAI', u:'/r/ClaudeAI/comments/1r2m8ma/...'},
    // ... more URLs
  ];
  const results = [];
  for (const item of urls) {
    try {
      const resp = await fetch('https://www.reddit.com' + item.u);
      const html = await resp.text();
      const vM = html.match(/>\s*([\d,.]+[KMB]?)\s*views?\s*</i);
      const cM = html.match(/comment-count="(\d+)"/);
      results.push({p:item.p, s:item.s, v:vM?vM[1]:'0', c:cM?cM[1]:'0'});
    } catch(e) {
      results.push({p:item.p, s:item.s, v:'err', c:'err'});
    }
  }
  localStorage.setItem('batch_result', JSON.stringify(results));
  return JSON.stringify(results);
})()
```

**Key regex patterns:**
- Views: `/>\s*([\d,.]+[KMB]?)\s*views?\s*</i` — captures the view count text (e.g., "1.5K", "196K", "57")
- Comments: `/comment-count="(\d+)"/` — captures comment count from `shreddit-post` element

If the result is truncated, read from localStorage in parts:
```javascript
JSON.parse(localStorage.getItem('batch_result')).slice(0, 15)
```

### Step 5: Update reports/reddit.md

For each post row, update the views (👁️) and comments (🗣️) columns:
- **Multi-subreddit posts**: Use ` • ` separator ordered by subreddit appearance (e.g., `1.5K • 316 • 102 • 58`)
- **Single-subreddit posts**: Just the value (e.g., `2.9K`)
- **Posts with 0 views across all subreddits**: These are removed/deleted posts. Flag them to the user and ask if they should be removed.
- **Posts with any subreddit having >50K views**: Prefix that specific value with 🚀 emoji (e.g., `🚀 196K • 1.7K` or `13K • 🚀 59K`)

### Step 6: Update README.md

The README shows only the **top N most recent posts** in a preview table (currently posts 41-38). Update the same columns (👁️ and 🗣️) for those posts in the README with the same format.

Also update the total count `REDDIT (N)` in both files if posts were added or removed.

### Step 7: Summary

Print a summary showing:
- Total posts updated
- Any posts flagged as removed (0 views)
- Any errors encountered during fetching

## Important Notes

- The `fetch()` approach works because it uses the user's authenticated Reddit session cookies
- Reddit returns HTML that contains view counts in `<span>` elements and comment counts in `shreddit-post` custom element attributes
- Some posts may show `0` views if they've been removed by mods — confirm with user before removing
- View counts use K/M/B suffixes (e.g., 1.5K = 1,500 views, 196K = 196,000 views)
- Always preserve the existing table structure and formatting
- The README.md uses ` • ` (with spaces) as separator between cross-post values in views and comments columns
- Only the last 80 posts are fetched for updated stats — older posts retain their existing values
