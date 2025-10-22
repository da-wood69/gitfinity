#!/usr/bin/env python3
"""
Daily GitHub Commit Script
Runs 8 times per day (every ~3 hours), creating 0-2 commits each run.
With adjusted weights, averages ~3-4 commits per day for realistic activity.
"""

import argparse
import os
import random
import subprocess
from datetime import datetime
from pathlib import Path


class DailyCommitter:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.activity_file = self.repo_path / "activity.log"

    def get_s_curve_commits(self):
        """
        Generate random number of commits (0-2) using weighted distribution.

        Since the workflow runs 8 times per day with these weights:
        - 60% chance of 0 commits (most runs do nothing)
        - 35% chance of 1 commit (occasionally active)
        - 5% chance of 2 commits (rare bursts)

        Expected: ~3-4 commits per day (0.45 commits/run * 8 runs)
        """
        # Weights adjusted for 8 runs per day to avoid too many commits
        weights = [60, 35, 5]  # 0, 1, 2 commits

        # Use weighted random choice
        commits = random.choices(range(3), weights=weights, k=1)[0]
        return commits

    def run_git_command(self, command):
        """Execute a git command and return the result."""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            print(f"Error output: {e.stderr}")
            return None

    def truncate_log_file(self, max_lines=100):
        """Keep only the last max_lines in the activity log."""
        if not self.activity_file.exists():
            return

        # Read all lines
        with open(self.activity_file, "r") as f:
            lines = f.readlines()

        # If we have more than max_lines, keep only the last max_lines
        if len(lines) > max_lines:
            with open(self.activity_file, "w") as f:
                f.writelines(lines[-max_lines:])
            print(f"Truncated log file to {max_lines} lines")

    def update_activity_file(self):
        """Update the activity log file with a timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create or append to activity file
        with open(self.activity_file, "a") as f:
            f.write(f"{timestamp} - Activity logged\n")

        # Truncate if needed
        self.truncate_log_file(max_lines=100)

        return timestamp

    def make_commit(self, commit_number):
        """Create a single commit."""
        timestamp = self.update_activity_file()

        # Stage the changes
        self.run_git_command(["git", "add", "activity.log"])

        # Create commit
        commit_message = f"Daily activity update #{commit_number} - {timestamp}"
        result = self.run_git_command(["git", "commit", "-m", commit_message])

        if result is not None:
            print(f"Commit #{commit_number} created: {commit_message}")
            return True
        return False

    def push_commits(self):
        """Push all commits to GitHub."""
        print("Pushing commits to GitHub...")
        result = self.run_git_command(["git", "push"])

        if result is not None:
            print("Successfully pushed to GitHub!")
            return True
        else:
            print("Failed to push to GitHub")
            return False

    def run(self, auto_push=True, test_mode=False):
        """Main execution: create 0-2 random commits and optionally push."""
        # Random number of commits using S-curve distribution
        if test_mode:
            num_commits = 2  # Always create 2 commits in test mode
            print(f"=== Daily GitHub Activity (TEST MODE) ===")
        else:
            num_commits = self.get_s_curve_commits()
            print(f"=== Daily GitHub Activity ===")

        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Commits to create: {num_commits}")
        print("=" * 30)

        if num_commits == 0:
            print("No commits this run. Skipping...")
            return

        # Create the commits
        # Note: No delays needed since workflow runs multiple times per day
        successful_commits = 0
        for i in range(1, num_commits + 1):
            if self.make_commit(i):
                successful_commits += 1

        print(f"\nCreated {successful_commits} commit(s)")

        # Push to GitHub if enabled
        if successful_commits > 0 and auto_push:
            self.push_commits()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create 0-8 random commits for daily GitHub activity"
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push commits to remote (useful for CI/CD)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: always create 2 commits instead of random (0-2)"
    )
    args = parser.parse_args()

    committer = DailyCommitter()
    committer.run(auto_push=not args.no_push, test_mode=args.test)
