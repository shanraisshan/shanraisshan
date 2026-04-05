# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

This is **shanraisshan's GitHub profile repo** — a living portfolio that displays GitHub repos, YouTube videos, social links, and a snapshot of recent Reddit activity on the profile page. The primary content is markdown with shields.io badges.

**Note:** All Reddit post tracking, GitHub star tracking, workflows, MCP servers, and the shayan-second-brain agent have been migrated to the [shayan-second-brain](https://github.com/shanraisshan/shayan-second-brain) repo.

## Key Files

- `README.md` — The GitHub profile page. Contains "Latest" (4 newest by posting date) and "Most Viewed" (5 posts with highest single-subreddit view count) Reddit tables, GitHub repos list, social links, and YouTube videos.
- `reports/sponsored-repos.md` — Curated list of company-sponsored GitHub repos and open-source AI coding tools.
- `!/` — Static assets directory: SVGs (mascots, badges, banners), profile image, YouTube thumbnails, icons.

## Badge Formatting Rules

All badges use shields.io.

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

## Git Commit Rules

When committing changes, **create separate commits per file**. Each file gets its own commit with a descriptive message specific to that file's changes.

## Hooks System

All 27 Claude Code hooks are configured in `.claude/settings.json`, each calling `.claude/hooks/scripts/hooks.py`. The hooks play audio feedback sounds for different events. Config toggles are in `.claude/hooks/config/hooks-config.json`.

## Last Updated Badge

In README.md after the "Recent Activity" heading. Uses PKT timezone:
```
TZ='Asia/Karachi' date '+%b %d, %Y %I:%M %p PKT'
```
URL-encode spaces as `_`, commas as `%2C`, colons as `%3A`.
