---
description: End-to-end workflow to fetch latest Reddit posts via MCP, add new posts to reports/reddit.md and update README.md
user-invocable: true
allowed-tools: Task, Read, Edit, Grep, Bash, Skill, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__javascript_tool
---

# Workflow: New Reddit Posts

This is an end-to-end workflow that fetches the latest Reddit posts, identifies new ones, and updates both `reports/reddit.md` and `README.md`.

---

## Step 1: Check Claude in Chrome Connection

Before proceeding, verify that the Claude in Chrome extension is connected and responsive.

1. Call `mcp__claude-in-chrome__tabs_context_mcp` (with `createIfEmpty: true`)
2. If the call succeeds and returns tab information → **proceed to Step 2**
3. If the call fails or returns an error → **stop the workflow** and tell the user:
   > "Claude in Chrome is not connected. Please make sure the Claude in Chrome extension is installed and active in your browser, then try again."

---

## Step 2: Read Existing Posts

Read `reports/reddit.md` to understand:
- The current highest S# (post number)
- All existing post titles (to detect duplicates)
- The exact table format used

Store this data for comparison in Step 4.

---

## Step 3: Call the Reddit Fetch Agent

Use the **Task tool** to launch the `workflow-reddit-new-agent`:

```
Task tool parameters:
  subagent_type: general-purpose
  prompt: |
    You are the Reddit Post Fetcher Agent. Follow the instructions in
    .claude/agents/workflows/workflow-reddit-new-agent.md exactly.
    Read that file first, then execute all phases and return the structured
    list of posts as specified in the Return Format section.
```

Wait for the agent to return the full list of grouped posts.

---

## Step 4: Identify New Posts and New Cross-Posts

Compare the agent's returned posts against the existing posts in `reports/reddit.md`:
- Match by **title** (case-insensitive, fuzzy match for minor differences)
- Any post from the agent's list that does NOT exist in the current report = **new post**
- For existing posts, compare subreddit links — if the agent found new subreddit cross-posts not in the report, flag them as **new cross-posts**

### 4a: Update Existing Posts with New Cross-Posts

For each existing post that has new cross-post subreddits:
1. Append the new subreddit link(s) to the Subreddit column with `(0 • 0)` inline — e.g., `[/NewSub](url) (0 • 0)`
2. The new subreddit entry goes at the END of the existing entries (it has 0 views, so it will be last after sorting)
3. Update the same post in `README.md` if it appears in the Latest or Most Viewed tables

If no new posts AND no new cross-posts are found, inform the user and stop.

---

## Step 5: Add New Posts to `reports/reddit.md`

For each new post (in chronological order, oldest first):

1. **Assign S#**: Increment from the current highest S# (e.g., if highest is 52, new posts start at 53)
2. **Format the row** using the 3-column table format:

```
| [S#] | [Post Title] | [/Sub1](url1) (0 • 0) [/Sub2](url2) (0 • 0) |
```

- **Subreddit column**: Each subreddit link is followed by `(views • comments)` inline — e.g., `[/ClaudeAI](url) (0 • 0)`
- Multiple subreddits are space-separated within the same column
- Views and comments are set to `0` for new posts (will be updated by the `reddit-update-stat-skill` later)

3. **Insert new rows** at the TOP of the table (after the header row), since they are the most recent posts
4. **Update the total count** in the heading: `## <img ...> REDDIT ([new count])`

---

## Step 6: Update `README.md`

Update the Reddit section in `README.md`:

### Latest Posts Table
- Replace the **Latest** table (currently shows the top 4 most recent posts) with the 4 newest posts by S# (descending)
- Use the exact same row format as `reports/reddit.md`

### Most Viewed Table
- Keep the **Most Viewed** table unchanged (it shows top 5 by views — new posts have 0 views so they won't appear here)

### Count
- Update `REDDIT ([count])` heading to match the new total from `reports/reddit.md`
- Update the `### <img ...> REDDIT ([count])` in README.md to match

---

## Step 7: Update "Last Updated" Badge

Update the **Last Updated** badge in `README.md` (located right after the `## Recent Activity` heading) with the current date/time in Pakistan Standard Time (PKT).

1. Get the current PKT time by running: `TZ='Asia/Karachi' date '+%b %d, %Y %I:%M %p PKT'`
2. URL-encode the date string for the shields.io badge:
   - Spaces → `_`
   - Commas → `%2C`
   - Colons → `%3A`
3. Replace the existing badge line with the updated one:

```
![Last Updated](https://img.shields.io/badge/Last_Updated-{encoded_date}-white?style=flat&labelColor=555)
```

For example, if the time is `Feb 25, 2026 10:44 AM PKT`, the badge URL becomes:
```
https://img.shields.io/badge/Last_Updated-Feb_25%2C_2026_10%3A44_AM_PKT-white?style=flat&labelColor=555
```

---

## Step 8: Summary

Print a summary:
- Number of new posts added
- List of new post titles with their assigned S#

---

## Step 9: Update View and Comment Counts

After new posts have been added, invoke the `workflow-reddit-update` skill using the **Skill tool** to fetch and update view counts and comment counts for all recent posts (including the newly added ones).

```
Skill tool parameters:
  skill: "reddit-update-stat-skill"
```

This skill requires Reddit to be open in a Chrome tab within the Claude in Chrome tab group. If the user does not have Reddit open, ask them to open any Reddit page before proceeding.

Wait for the skill to complete. It will update the inline view and comment counts for the last 80 posts in both `reports/reddit.md` and `README.md`.

---

## Step 10: Commit Changes

After all updates are complete, invoke the `git:commit` command using the **Skill tool** to stage and commit all changes.

```
Skill tool parameters:
  skill: "git:commit"
```

This will stage `reports/reddit.md`, `README.md`, and any modified workflow/skill files, then create a commit with a descriptive message.

---

## Important Rules

1. **Do NOT modify existing post titles or S#** — only add new posts or append new cross-post subreddit links to existing posts (view/comment updates are handled by Step 9)
2. **Preserve exact table formatting** — match the existing column alignment and separators
3. **Cross-post grouping** — if a post appears in multiple subreddits, it's ONE row with multiple subreddit links
4. **Sequential S# numbering** — never skip or reuse numbers
5. **The ` • ` separator** — used inline within parentheses to separate views and comments (e.g., `(0 • 0)`)
6. **GitHub stars badge colors** — when adding new repos to the GitHub section, use color-coded star badges: `color=black` (< 100 stars), `color=3FB950` (>= 100), `color=F09000` (>= 500), `color=FF5252` (>= 1000). Use `labelColor=white` for all.
