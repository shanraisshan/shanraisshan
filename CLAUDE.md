# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

This is **shanraisshan's GitHub profile repo** — a living portfolio that displays Reddit post activity, GitHub repos, LinkedIn posts, and YouTube videos on the profile page. The primary content files are markdown with shields.io badges, and the repo has automated workflows for tracking Reddit post stats (views, comments) and promotions.

## Key Files

- `README.md` — The GitHub profile page. Contains "Latest" (4 newest by posting date) and "Most Viewed" (5 posts with highest single-subreddit view count) Reddit tables, GitHub repos list, social links, and YouTube videos.
- `reports/reddit.md` — Complete Reddit post log (157+ posts). Each row has S#, title, and subreddit cross-posts with `(views • comments)` stats. Posts are numbered sequentially, newest first.
- `reports/reddit-promotion.md` — Tracks which Reddit posts link back to specific repos (claude-code-best-practice, claude-code-hooks, codex-cli-best-practice, codex-cli-hooks). Categorized by promotion type.
- `reports/sponsored-repos.md` — Curated list of company-sponsored GitHub repos and open-source AI coding tools.
- `!/` — Static assets directory: SVGs (mascots, badges, banners), profile image, YouTube thumbnails, icons.

## Workflows (Slash Commands)

- `/workflow-reddit` — Fetches new Reddit posts + updates views/comments for ALL posts. Uses AppleScript to scrape Reddit profile page in Chrome. Requires Chrome open and logged into Reddit. Takes ~1 min. Updates both `reports/reddit.md` and `README.md`.
- `/workflow-reddit-promotion` — Detects new posts in reddit.md not yet in reddit-promotion.md, fetches post descriptions via Reddit MCP, classifies promotion type, adds to correct section.
- `/commit` — Stages and commits changes to reddit.md, README.md, and workflow files.

## MCP Servers

Configured in `.mcp.json`:
- **reddit-mcp-server** — Remote HTTP MCP at `http://144.91.76.33:8080/mcp`. Provides `browse_subreddit`, `get_post_details`, `search_reddit`, `user_analysis`.
- **reddit-stats** — Local stdio MCP (`reddit-mcp/server.py`). Uses AppleScript + Chrome to fetch Reddit post views/comments from rendered pages. Max 25 URLs per call.

## Badge Formatting Rules

All badges use shields.io. Color thresholds are documented in `.claude/projects/-Users-shayanraees-Documents-Github-shanraisshan/memory/MEMORY.md` but the key rules:

### Reddit Views (badges at >= 50K)
- `>= 50K`: green `3FB950` | `> 100K`: orange `F09000` | `> 200K`: red `FF5252`
- `>= 500K`: convert to millions (0.5M, 1M, etc.), red `FF5252`
- Format: `![VALUE](https://img.shields.io/badge/%F0%9F%91%80-VALUE-COLOR?style=flat&labelColor=white)`

### Reddit Comments (badges at > 50)
- `> 50`: green `3FB950` | `> 100`: orange `F09000` | `> 500`: red `FF5252`
- Format: `![VALUE](https://img.shields.io/badge/%F0%9F%97%A3%EF%B8%8F-VALUE-COLOR?style=flat&labelColor=white)`

### GitHub Stars
- `< 100`: black | `>= 100`: green `3FB950` | `>= 500`: orange `F09000` | `>= 1000`: red `FF5252`
- Format: `![Stars](https://img.shields.io/github/stars/shanraisshan/REPO?style=flat&label=%E2%98%85&labelColor=white&color=COLOR)`

## Reddit Post Table Format

Each row in `reports/reddit.md`: `| S# | Post Title | [/Sub](url) (views • comments) [/Sub2](url2) (views • comments) |`

Key rules:
- S# is sequential, never skip or reuse
- Cross-posts of the same title = ONE row with multiple subreddit links
- Subreddits sorted by views (highest first) within each row
- The `(views • comments)` uses ` • ` as separator
- New posts go at the TOP of the table
- Zero-view safeguard: never downgrade a non-zero view count to zero

## Git Commit Rules

When committing changes, **create separate commits per file**. Do NOT bundle multiple file changes into a single commit. Each file gets its own commit with a descriptive message specific to that file's changes.

For example, if `README.md`, `reports/reddit.md`, and a workflow file all changed:
- Commit 1: `git add README.md` → commit with README-specific message
- Commit 2: `git add reports/reddit.md` → commit with reddit.md-specific message
- Commit 3: `git add .claude/commands/workflows/workflow-reddit.md` → commit with workflow-specific message

This makes the git history cleaner and easier to review, revert, or cherry-pick individual changes.

## Hooks System

All 27 Claude Code hooks are configured in `.claude/settings.json`, each calling `.claude/hooks/scripts/hooks.py`. The hooks play audio feedback sounds for different events. Config toggles are in `.claude/hooks/config/hooks-config.json`.

## Last Updated Badge

In README.md after the "Recent Activity" heading. Uses PKT timezone:
```
TZ='Asia/Karachi' date '+%b %d, %Y %I:%M %p PKT'
```
URL-encode spaces as `_`, commas as `%2C`, colons as `%3A`.
