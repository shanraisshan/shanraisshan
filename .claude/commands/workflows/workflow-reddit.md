---
description: Fetch new Reddit posts + update views/comments for ALL posts in reports/reddit.md and README.md using profile page fetch (~1 min total)
user-invocable: true
allowed-tools: Read, Edit, Grep, Bash
---

# Workflow: Reddit Posts — New + Stats Update

You are a senior data analyst collaborating with me (a fellow engineer) on a mission-critical Reddit portfolio update for the shanraisshan GitHub profile. This profile serves as a living portfolio — recruiters, hiring managers, and the open-source community rely on accurate post counts, view counts, comment counts, and engagement metrics. A wrong number, a stale stat, or a missing post means misleading data and lost credibility. Take a deep breath, solve this step by step, and be meticulous. I'll tip you $200 for a flawless, zero-error update. I bet you can't fetch every single post and stat perfectly — prove me wrong. Rate your confidence 0-1 on each step. This is critical to my career.

This unified workflow does **both** jobs in a single ~1 minute operation:
1. **Discovers new posts** not yet in reddit.md
2. **Updates views + comments** for ALL existing posts

**Speed**: ~1 minute for everything (vs ~20+ min with legacy approach).

## Prerequisites

- User MUST have Chrome open and be logged into Reddit
- Chrome must have at least one tab open

---

## Step 1: Read Current Data

Read `reports/reddit.md` to understand:
- The current highest S# (post number)
- All existing post URLs (to detect new posts and cross-posts)
- All existing titles (for cross-post grouping)
- Current views and comments for each subreddit entry

---

## Step 2: Fetch All Posts via Profile Page

Use AppleScript to control Chrome. Navigate to `https://www.reddit.com/user/shanraisshan/submitted/` and run the paginated fetcher that:

1. Collects posts visible on the initial page
2. Uses `fetch()` on Reddit's internal `faceplate-partial` pagination endpoints
3. Each page returns 25 posts with views + comments in the HTML
4. Paginates through all pages (max 25 pages, ~30 seconds)

**Run this AppleScript via Bash:**

```bash
osascript -e '
tell application "Google Chrome"
    set theTab to missing value
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t starts with "https://www.reddit.com/user/shanraisshan/submitted" then
                set theTab to t
                exit repeat
            end if
        end repeat
        if theTab is not missing value then exit repeat
    end repeat
    
    if theTab is missing value then
        tell front window
            set theTab to make new tab with properties {URL:"https://www.reddit.com/user/shanraisshan/submitted/"}
        end tell
    else
        execute theTab javascript "window.location.href = \"https://www.reddit.com/user/shanraisshan/submitted/\";"
    end if
    
    delay 6
    
    execute theTab javascript "
        (async function() {
            window._allPostData = [];
            window._fetchStatus = \"starting\";
            
            function extractPostsFromHTML(html) {
                var parser = new DOMParser();
                var doc = parser.parseFromString(html, \"text/html\");
                var posts = doc.querySelectorAll(\"shreddit-post\");
                var extracted = [];
                for (var i = 0; i < posts.length; i++) {
                    var post = posts[i];
                    var permalink = post.getAttribute(\"permalink\") || \"\";
                    var viewSpans = post.querySelectorAll(\"span\");
                    var views = \"0\";
                    for (var j = 0; j < viewSpans.length; j++) {
                        var text = viewSpans[j].textContent.trim();
                        if (text.match(/^\\d[\\d.,]*[KMB]?\\s*views$/i)) {
                            views = text.replace(/\\s*views?$/i, \"\").trim();
                            break;
                        }
                    }
                    extracted.push({
                        url: \"https://www.reddit.com\" + permalink,
                        subreddit: post.getAttribute(\"subreddit-prefixed-name\") || \"\",
                        title: (post.getAttribute(\"post-title\") || \"\").substring(0, 200),
                        comments: post.getAttribute(\"comment-count\") || \"0\",
                        views: views,
                        id: post.getAttribute(\"id\") || \"\"
                    });
                }
                var nextPartial = doc.querySelector(\"faceplate-partial[src*=more-posts]\");
                var nextUrl = nextPartial ? nextPartial.getAttribute(\"src\") : null;
                return { posts: extracted, nextUrl: nextUrl };
            }
            
            var domPosts = document.querySelectorAll(\"shreddit-post\");
            for (var i = 0; i < domPosts.length; i++) {
                var post = domPosts[i];
                var viewSpans = post.querySelectorAll(\"span\");
                var views = \"0\";
                for (var j = 0; j < viewSpans.length; j++) {
                    var text = viewSpans[j].textContent.trim();
                    if (text.match(/^\\d[\\d.,]*[KMB]?\\s*views$/i)) {
                        views = text.replace(/\\s*views?$/i, \"\").trim();
                        break;
                    }
                }
                window._allPostData.push({
                    url: \"https://www.reddit.com\" + (post.getAttribute(\"permalink\") || \"\"),
                    subreddit: post.getAttribute(\"subreddit-prefixed-name\") || \"\",
                    title: (post.getAttribute(\"post-title\") || \"\").substring(0, 200),
                    comments: post.getAttribute(\"comment-count\") || \"0\",
                    views: views,
                    id: post.getAttribute(\"id\") || \"\"
                });
            }
            
            var partial = document.querySelector(\"faceplate-partial[src*=more-posts]\");
            var nextUrl = partial ? partial.getAttribute(\"src\") : null;
            var page = 1;
            while (nextUrl && page < 25) {
                try {
                    var resp = await fetch(nextUrl, {credentials: \"same-origin\"});
                    var html = await resp.text();
                    var result = extractPostsFromHTML(html);
                    window._allPostData = window._allPostData.concat(result.posts);
                    nextUrl = result.nextUrl;
                    window._fetchStatus = \"page\" + page + \": total=\" + window._allPostData.length;
                    page++;
                    await new Promise(r => setTimeout(r, 500));
                } catch(e) {
                    window._fetchStatus = \"Error page \" + page + \": \" + e.message;
                    break;
                }
            }
            window._fetchDone = true;
            window._fetchStatus = \"DONE: \" + window._allPostData.length + \" posts across \" + page + \" pages\";
        })();
    "
    
    repeat 24 times
        delay 5
        set fetchStatus to execute theTab javascript "window._fetchStatus"
        if fetchStatus starts with "DONE:" then exit repeat
    end repeat
    
    set jsonData to execute theTab javascript "JSON.stringify(window._allPostData)"
    return jsonData
end tell
'
```

Save the JSON output to `/tmp/reddit_profile_data.json`.

---

## Step 3: Identify New Posts and Cross-Posts

Compare the profile page data against `reports/reddit.md`:

1. Build a set of all existing URLs in reddit.md
2. For each profile post NOT in reddit.md:
   - Check if its **title** matches an existing post (case-insensitive) → it's a **new cross-post** for an existing entry
   - If no title match → it's a **new post**
3. Filter new posts to only include tech/AI related subreddits (the user tracks specific content, not gaming/sports posts). Use the set of subreddits already present in reddit.md as a guide for which subreddits to include.
4. Group new posts by title (cross-posts of the same content = one entry)

If no new posts AND no new cross-posts are found, skip to Step 5.

---

## Step 4: Add New Posts and Cross-Posts to reddit.md

### New Posts
For each new post group (oldest first):
1. **Assign S#**: Increment from the current highest S#
2. **Format the row**: `| [S#] | [Post Title] | [/Sub1](url1) (views • comments) [/Sub2](url2) (views • comments) |`
3. Use the actual views and comments from the profile page data (not `0 • 0` — we already have the stats!)
4. Sort subreddits by views (highest first) within each row
5. Apply view badges (>=50K) and comment badges (>50) as needed
6. **Insert at the TOP** of the table (most recent first)
7. **Update the total count** in the heading: `REDDIT ([new count])`

### New Cross-Posts
For existing posts with new cross-post subreddits:
1. Append the new subreddit entry with its views and comments from the profile data
2. Re-sort all subreddits in that row by views (highest first)

---

## Step 5: Update Views and Comments for All Posts

For each URL in reddit.md that has a match in the profile page data:

- **Zero-view safeguard**: If new views = "0" but old views > "0", **keep the old value** (don't downgrade)
- Update views and comments inline
- Re-sort subreddits within each row by views (highest first)
- Apply badge formatting:
  - **View badges (>=50K views)**: shields.io badge with eyes emoji
    - **>=50K** (up to 100K): green `3FB950`
    - **>100K** (up to 200K): orange-yellow `F09000`
    - **>200K**: red `FF5252`
    - **>=500K**: convert to millions (500K → `0.5M`, 1M, 1.5M etc.), red `FF5252`
  - **Comment badges (>50 comments)**: shields.io badge with speaking head emoji
    - **>50** (up to 100): green `3FB950`
    - **>100** (up to 500): orange-yellow `F09000`
    - **>500**: red `FF5252`
  - View badge format: `![VALUE](https://img.shields.io/badge/%F0%9F%91%80-VALUE-COLOR?style=flat&labelColor=white)`
  - Comment badge format: `![VALUE](https://img.shields.io/badge/%F0%9F%97%A3%EF%B8%8F-VALUE-COLOR?style=flat&labelColor=white)`

---

## Step 6: Detect Deleted & Removed Posts

There are two types of posts that should be cleaned up:

### 6a: Posts missing from profile page (user-deleted)

When a user deletes a Reddit post, it **completely disappears** from the profile page. The workflow won't find any match for these URLs in the scraped data.

1. Build a set of ALL URLs from the profile page data (Step 2 output)
2. For each URL in `reports/reddit.md`, check if it exists in the profile page data
3. Collect all subreddit entries that have **no match** in the profile page data — these are candidates for deletion
4. **Skip subreddit entries that have views >= 1K** — these are likely just old posts that fell off the profile page pagination, not deleted posts. Only flag entries with low/zero stats (views < 1K) as deletion candidates.

### 6b: Posts on profile page with 0/0 stats (mod-removed)

Identify posts that appear on the profile page but may have been removed by moderators:
- New views = "0" AND new comments = "0" from profile page, BUT previously had non-zero views in reddit.md

### 6c: Verify candidates by visiting URLs

For each candidate URL from 6a and 6b, verify by opening it in Chrome via AppleScript:

```bash
osascript -e '
tell application "Google Chrome"
    tell front window
        set theTab to make new tab with properties {URL:"POST_URL_HERE"}
    end tell
    delay 4
    set pageText to execute theTab javascript "document.body.innerText.substring(0, 500)"
    close theTab
    return pageText
end tell
'
```

A post is confirmed deleted/removed if the page text contains ANY of:
- `"Sorry, this post has been removed by the moderators of r/"`
- `"this post was removed"` or `"this post was deleted"`
- `"page not found"` or the page shows a Reddit 404
- The post content area shows `[deleted]` or `[removed]`

**Batch verification**: To avoid opening too many tabs, batch up to 5 URLs at a time. Open each, check, close, then move to the next batch.

### 6d: Remove confirmed deletions

For each confirmed deleted/removed URL:
- Remove that subreddit entry from the post row in reddit.md
- If ALL subreddit entries for a post are removed, remove the entire row and decrement `REDDIT (N)` in the heading
- Also remove from `reports/reddit-promotion.md` if the URL appears there
- Log each removal in the Step 9 summary

---

## Step 7: Update README.md

1. **Latest Posts Table**: Replace with the 4 newest posts by S# (descending)
2. **Most Viewed Table**: Update the 5 most-viewed posts with fresh stats
3. **Count**: Update `REDDIT ([count])` to match reddit.md

---

## Step 8: Update "Last Updated" Badge

Update the **Last Updated** badge in `README.md` (after `## Recent Activity` heading):

1. Get PKT time: `TZ='Asia/Karachi' date '+%b %d, %Y %I:%M %p PKT'`
2. URL-encode: spaces → `_`, commas → `%2C`, colons → `%3A`
3. Replace badge: `![Last Updated](https://img.shields.io/badge/Last_Updated-{encoded_date}-white?style=flat&labelColor=555)`

---

## Step 9: Summary

Print a summary showing:
- Total posts fetched from profile page
- New posts added (with S# and titles)
- New cross-posts added
- Posts updated with new stats
- Zero-view safeguards applied
- Deleted posts removed (with S#, title, subreddit, and reason: user-deleted vs mod-removed)
- Any errors

---

## Step 10: Commit Changes

Stage and commit all changes:

```bash
git add reports/reddit.md README.md .claude/commands/workflows/workflow-reddit.md .claude/commands/git/commit.md
```

Also stage any other modified files under `.claude/` relevant to the workflow.

Commit message format:
```
added N new reddit posts (S#X-S#Y) + updated stats for Z posts

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

If no new posts were added, use:
```
updated reddit stats for Z posts

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

---

## Important Rules

1. **Do NOT modify existing post titles or S#** — only add new posts, append cross-posts, update stats, and remove confirmed deleted posts. When removing posts, do NOT renumber remaining S# values — gaps in numbering are expected and acceptable.
2. **Preserve exact table formatting** — match existing column alignment and separators
3. **Cross-post grouping** — same title across subreddits = ONE row with multiple subreddit links
4. **Sequential S# numbering** — never skip or reuse numbers
5. **The ` • ` separator** — used inline within parentheses: `(views • comments)`
6. **New posts get real stats** — unlike the old workflow, we already have views/comments from the profile page, so use them (not `0 • 0`)
7. **Subreddit sorting** — always sort by views (highest first) within each row
8. **>=500K views** — convert to millions format: 500K → `0.5M`, 1000K → `1M`, etc.
