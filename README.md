# gitfinity

Automated daily GitHub activity generator that creates ~3-4 random commits per day to maintain your GitHub contribution graph.

## Features

- **Truly random timing**: 8 scheduled runs per day with 0-15 minute random delays for unpredictable commit times
- **Natural spread**: Commits distributed every ~3 hours throughout the entire day (0:00, 3:00, 6:00, 9:00, 12:00, 15:00, 18:00, 21:00 UTC)
- **Smart commit distribution**: Uses weighted algorithm where most runs create 0 commits, some create 1, rarely 2
- **Efficient execution**: Short delays (0-15 min) don't waste GitHub Actions time limits
- **Realistic patterns**: Averages ~3-4 commits per day with natural variation
- **Automatic log management**: Keeps only the last 100 lines to prevent file bloat
- **Fully automated**: Uses GitHub Actions (no server required, no costs)
- **Simple activity logging**: Tracks timestamps in activity.log

## How It Works

The program uses GitHub Actions workflows that run **8 times per day** (every ~3 hours):
- 🌙 Midnight: 0:00 UTC (± 0-15 min)
- 🌃 Late night: 3:00 UTC (± 0-15 min)
- 🌅 Early morning: 6:00 UTC (± 0-15 min)
- ☕ Morning: 9:00 UTC (± 0-15 min)
- 🌞 Noon: 12:00 UTC (± 0-15 min)
- 🌤️ Afternoon: 15:00 UTC (± 0-15 min)
- 🌆 Evening: 18:00 UTC (± 0-15 min)
- 🌇 Night: 21:00 UTC (± 0-15 min)

Each run adds a random 0-15 minute delay before executing, adding natural variation without wasting GitHub Actions time!

Each run then executes a Python script that:

1. Uses weighted distribution to select 0-2 commits:
   - 60% chance: 0 commits (most runs do nothing)
   - 35% chance: 1 commit (occasional activity)
   - 5% chance: 2 commits (rare bursts)
2. For each commit:
   - Updates the `activity.log` file with a timestamp
   - Creates a git commit
3. Automatically truncates the log file to 100 lines to prevent bloat
4. Pushes all commits to GitHub

**Result:** ~3-4 commits per day on average, naturally spread throughout 24 hours!

## Requirements

Just a GitHub account! Everything else runs in GitHub Actions (no installation, no server, no costs).

## Setup

**Quick Start:**

1. **Use this repository as a template** (⚠️ **IMPORTANT**: Do NOT fork!)
   - Click the green **"Use this template"** button at the top right of this page
   - Select **"Create a new repository"**
   - Choose a name for your repository (e.g., `my-github-activity`)
   - Make sure it's set to **Public** (required for contribution graph)
   - Click **"Create repository"**

   **Why not fork?** Commits in forked repositories don't count toward your GitHub contribution graph!

2. **Enable GitHub Actions**:
   - Go to your new repository on GitHub
   - Click the "Actions" tab
   - Click the green "I understand my workflows, go ahead and enable them" button (if prompted)

3. **Configure workflow permissions**:
   - Go to **Settings** → **Actions** → **General**
   - Scroll down to **Workflow permissions**
   - Select **"Read and write permissions"**
   - Check **"Allow GitHub Actions to create and approve pull requests"** (optional)
   - Click **Save**

4. **Activate the workflow**:

   - Go to **Actions** tab → **"Daily GitHub Activity"** workflow
   - Click **"Run workflow"** → **"Run workflow"** button to test it immediately
   - The scheduled runs will start automatically after the first manual run

5. **Verify it's working**:
   - Check the **Actions** tab for successful workflow runs
   - Look for new commits appearing in `activity.log`
   - Check your contribution graph after 24 hours (GitHub may take time to update)

**✅ Why commits will count:**
- Commits use your GitHub noreply email (automatically configured)
- Repository created from template (not a fork)
- Commits made to default branch (main)
- Repository is public

### Advanced Configuration (Optional)

#### Customize the schedule

Edit `.github/workflows/daily-commit.yml` lines 7-14:
```yaml
- cron: '0 0 * * *'   # 12:00 AM UTC
- cron: '0 3 * * *'   # 3:00 AM UTC
- cron: '0 6 * * *'   # 6:00 AM UTC
- cron: '0 9 * * *'   # 9:00 AM UTC
- cron: '0 12 * * *'  # 12:00 PM UTC
- cron: '0 15 * * *'  # 3:00 PM UTC
- cron: '0 18 * * *'  # 6:00 PM UTC
- cron: '0 21 * * *'  # 9:00 PM UTC
```
You can add/remove runs or change the times. Use [crontab.guru](https://crontab.guru/) for help.

**Note:** If you reduce the number of scheduled runs, consider adjusting the commit weights in `daily_commit.py` to maintain desired daily commit counts.

**Manual Testing (Optional):**

You can test the script locally:
```bash
# Run with automatic push
python3 daily_commit.py

# Run without pushing (commits only)
python3 daily_commit.py --no-push

# Test mode: always create 2 commits (useful for testing)
python3 daily_commit.py --test --no-push
```

## Customization

### Change random delay window

Edit `.github/workflows/daily-commit.yml` line 27:
```bash
DELAY=$((RANDOM % 900))  # 900 seconds = 15 minutes
```
Change `900` to adjust the randomization window:
- `300` = 0-5 minutes
- `600` = 0-10 minutes
- `900` = 0-15 minutes ⭐ Default
- `1800` = 0-30 minutes

### Change commit distribution per run

Edit `daily_commit.py` around line 33 in the `get_s_curve_commits()` method:
```python
weights = [60, 35, 5]  # 0, 1, 2 commits per run
```
Higher numbers = more likely. Example: `[50, 45, 5]` makes commits slightly more frequent.

### Change maximum commits per run

To change the range (currently 0-2), edit line 33:
```python
commits = random.choices(range(3), weights=weights, k=1)[0]
```
Change `range(3)` to `range(4)` for 0-3, and update weights accordingly.

### Change log file size limit

Edit `daily_commit.py` around line 74:
```python
self.truncate_log_file(max_lines=100)  # Change max_lines value
```

### Change commit message format

Edit `daily_commit.py` around line 86:
```python
commit_message = f"Daily activity update #{commit_number} - {timestamp}"
```

## Probability Distribution

With the default settings:

**Per run (0-2 commits):**
- 0 commits: 60% chance (most runs do nothing)
- 1 commit: 35% chance ⭐ Occasional activity
- 2 commits: 5% chance (rare bursts)

**Per day (8 runs):**
- Expected average: ~3-4 commits per day
- Minimum: 0 commits (all runs skip)
- Maximum: 16 commits (all runs create 2 - very unlikely!)
- Timing: Random within eight 15-minute windows spread across 24 hours

**Example day:**
```
0:08 AM  → 0 commits (skipped)
3:12 AM  → 1 commit
6:02 AM  → 0 commits (skipped)
9:14 AM  → 0 commits (skipped)
12:05 PM → 1 commit
3:11 PM  → 0 commits (skipped)
6:09 PM  → 2 commits (rare!)
9:03 PM  → 1 commit

Total: 5 commits at unpredictable times!
```

## License

MIT

## Notes

This is meant for maintaining GitHub activity and learning automation. The commits are real and will appear in your contribution graph.

**Realism features:**
- ✅ Commits happen at random times (not predictable patterns)
- ✅ Distributed across 8 time windows throughout the day
- ✅ Variable commit count using weighted distribution
- ✅ Efficient execution (0-15 min delays)
- ✅ Automatic log file management

**Contribution graph requirements:**
- ✅ Uses your GitHub account email (via noreply address)
- ✅ Commits to default branch (main)
- ✅ Must use as template, NOT fork
- ✅ Repository must be public

The randomization ensures your activity looks natural and human-like!
