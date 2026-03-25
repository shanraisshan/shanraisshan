---
description: Check for new Reddit posts in reddit.md, fetch their descriptions, and add to the correct section in reddit-promotion.md
user-invocable: true
allowed-tools: Read, Edit, Grep, Bash, mcp__reddit-mcp-server__get_post_details
---

# Workflow: Reddit Promotion Report Update

This workflow detects new Reddit posts in `reports/reddit.md` that are not yet tracked in `reports/reddit-promotion.md`, fetches their descriptions via the Reddit MCP server, and adds them to the correct repo section if they link one of the tracked repos.

---

## Tracked Repos

The report tracks promotion posts for these 4 repos. Each has specific keywords to detect in post descriptions:

| Repo | Section Header | Keywords in Post Description |
|---|---|---|
| claude-code-best-practice | `## ...claude-code-best-practice` | `claude-code-best-practice`, `shanraisshan/claude-code-best-practice` |
| claude-code-hooks | `## ...claude-code-hooks` | `claude-code-hooks`, `claude-code-voice-hooks`, `shanraisshan/claude-code-hooks`, `shanraisshan/claude-code-voice-hooks` |
| codex-cli-best-practice | `## ...codex-cli-best-practice` | `codex-cli-best-practice`, `shanraisshan/codex-cli-best-practice` |
| codex-cli-hooks | `## ...codex-cli-hooks` | `codex-cli-hooks`, `codex-cli-voice-hooks`, `shanraisshan/codex-cli-hooks`, `shanraisshan/codex-cli-voice-hooks` |

---

## Step 1: Collect All S# Numbers Already in reddit-promotion.md

Read `reports/reddit-promotion.md` and extract every S# that appears in any table row across all sections. Store as a set of known S# numbers.

---

## Step 2: Collect All Posts from reddit.md

Read `reports/reddit.md` and extract every post row: S#, title, and all subreddit URLs with their views.

---

## Step 3: Identify New Posts

Compare the two sets. Any S# in reddit.md that is NOT in the known set from Step 1 = **candidate post**. Also check posts that already exist but may have new cross-post subreddits added.

If no new candidates found, inform the user and stop.

---

## Step 4: Fetch Post Descriptions

For each candidate post, pick the **first subreddit URL** from reddit.md and call:

```
mcp__reddit-mcp-server__get_post_details
  url: <reddit_url>
  comment_limit: 0
  max_top_comments: 0
```

Extract the `content` field from the response — this is the post description/body text.

---

## Step 5: Classify Each Post

Check the post description (content) for keywords from the Tracked Repos table above. A post can match **multiple repos** (e.g., S#41 links both claude-code-best-practice and claude-code-hooks).

If a post description does NOT contain any of the tracked repo keywords → **skip it** (it doesn't promote any tracked repo).

For each match, determine which **Type** it belongs to within that repo's section:

### For claude-code-best-practice:
- **Type 1** — Description links to a specific `reports/*.md` file inside the repo
- **Type 2** — Description mentions the repo as supplementary info (mid-sentence link, "best practices" reference)
- **Type 3** — Description is about a repo milestone (star count, trending, etc.)
- **Type 4** — Description is about a different repo but name-drops claude-code-best-practice

### For claude-code-hooks:
- **Type 1** — Hook update post with repo linked as implementation reference
- **Type 2** — Feature showcase with hooks repo as the project being demoed
- **Type 3** — Cross-pollination (hooks repo mentioned while promoting other tools)

### For codex-cli-best-practice:
- **Type 1** — Direct repo promotion
- **Type 2** — Comparison post linking both claude-code-best-practice and codex-cli-best-practice

### For codex-cli-hooks:
- **Type 1** — Direct repo promotion

If classification is ambiguous, default to the most specific type that fits.

---

## Step 6: Format and Insert the New Row

For each classified post, build the table row in the existing format:

```
| S# | Post Title | Subreddit (Views) | How Repo Was Linked |
```

### Subreddit (Views) column:
- Use all subreddit cross-posts from reddit.md for this S#
- Format: `[/SubName](url) (views)` separated by ` • `
- Ordered by views descending (matching reddit.md order)

### Views badge rules (>= 50K):
- **>= 50K**: `![VALUE](https://img.shields.io/badge/%F0%9F%91%80-VALUE-3FB950?style=flat&labelColor=white)` (green)
- **> 100K**: color `F09000` (orange)
- **> 200K**: color `FF5252` (red)
- **< 50K**: plain text (e.g., `23K`)

### Last column:
- Summarize HOW the repo was referenced in the post description — use quotes from the actual content, matching the style of existing entries

### Sorting / Insertion point:
- Insert into the correct Type table within the correct repo section
- Maintain **descending view order** — sort by the **first subreddit's view count** (the highest view subreddit), not the total. For example, a post with `/ClaudeAI (210K) • /claude (3.6K)` sorts by 210K, and a post with `/ClaudeAI (20K) • /ChatGPT (6.1K)` sorts by 20K. The 210K post comes first.
- When a view is a badge (e.g., `![210K](badge_url)`), parse the numeric value from the badge text, treating `K` as thousands
- If the Type table header uses a different last column name (e.g., "Repo Link In Post", "Content", "How Main Repo Was Referenced"), match it

---

## Step 7: Summary

Print a summary:
- Number of new posts added to reddit-promotion.md
- For each: S#, title, which repo section(s), which type(s)
- Any posts that were skipped (no repo link found in description)

---

## Important Rules

1. **Never modify existing rows** — only add new ones
2. **Never remove or reorder existing content** — only insert new rows into existing tables
3. **Match the exact formatting** of existing rows in each table
4. **A post can appear in multiple repo sections** — if S#41 links both claude-code-best-practice and claude-code-hooks, it should have a row in both sections
5. **Do not add backtick formatting** to any cell content — use plain text
6. **Fetch the description from the first subreddit URL only** — cross-posts share the same description
7. **If a post has 0 views** (newly added to reddit.md), still add it with the view counts from reddit.md
