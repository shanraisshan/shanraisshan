---
description: Stage and commit all changes to reports/reddit.md, README.md, and workflow files
user-invocable: true
allowed-tools: Bash
---

# Git Commit

Commit all current changes related to Reddit post updates.

## Steps

1. Run `git status` to see all modified files
2. Stage the relevant files:
   ```
   git add reports/reddit.md README.md .claude/commands/workflows/workflow-reddit-new.md .claude/commands/git/commit.md .claude/skills/reddit-update-stat-skill/SKILL.md
   ```
   Also stage any other modified files under `.claude/` that are relevant to the workflow.
3. Create a commit with a descriptive message summarizing what changed:
   - Number of posts updated (views/comments)
   - Any new posts added
   - Any new cross-post subreddit links added
   - Any workflow/skill changes

   Use this format:
   ```
   git commit -m "$(cat <<'EOF'
   updated reddit stats

   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
   EOF
   )"
   ```
4. Run `git status` after the commit to verify success
