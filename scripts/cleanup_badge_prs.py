#!/usr/bin/env python3
"""
Cleanup script to close unnecessary badge update PRs
This script will:
1. List all open PRs
2. Find badge update PRs
3. Close them (and optionally delete their branches)
"""
import subprocess
import json
import argparse
import sys

def get_open_badge_prs():
    """Get list of open PRs that are badge updates"""
    try:
        # List all open PRs
        result = subprocess.run(
            ["gh", "pr", "list", "--json", "number,title,headRefName,author", "--state", "open"],
            capture_output=True,
            text=True,
            check=True
        )
        
        prs = json.loads(result.stdout)
        badge_prs = []
        
        for pr in prs:
            # Check if it's a badge update PR
            if (pr['title'].lower() == "update test status badge" and 
                pr['author']['login'] == "github-actions[bot]"):
                badge_prs.append(pr)
        
        return badge_prs
    except subprocess.CalledProcessError as e:
        print(f"Error getting PRs: {e}")
        return []

def close_pr(pr_number, delete_branch=True):
    """Close a PR and optionally delete its branch"""
    try:
        print(f"Closing PR #{pr_number}...")
        subprocess.run(
            ["gh", "pr", "close", str(pr_number), "--comment", "Closing outdated badge update PR"],
            check=True
        )
        
        if delete_branch:
            # Get the branch name
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", "headRefName"],
                capture_output=True,
                text=True,
                check=True
            )
            pr_data = json.loads(result.stdout)
            branch_name = pr_data.get('headRefName')
            
            if branch_name:
                print(f"  Deleting branch: {branch_name}")
                try:
                    subprocess.run(
                        ["git", "push", "origin", "--delete", branch_name],
                        check=True,
                        capture_output=True
                    )
                except subprocess.CalledProcessError:
                    print(f"  Failed to delete branch {branch_name} (might be protected or already deleted)")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Failed to close PR #{pr_number}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Cleanup unnecessary badge update PRs")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    parser.add_argument("--keep-branches", action="store_true", help="Don't delete branches after closing PRs")
    parser.add_argument("--keep-latest", action="store_true", help="Keep the most recent badge update PR open")
    args = parser.parse_args()
    
    # Check if gh CLI is available
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: GitHub CLI (gh) is not installed or not in PATH")
        print("Install it from: https://cli.github.com/")
        sys.exit(1)
    
    # Get badge PRs
    badge_prs = get_open_badge_prs()
    
    if not badge_prs:
        print("No open badge update PRs found.")
        return
    
    print(f"Found {len(badge_prs)} open badge update PRs:")
    for pr in badge_prs:
        print(f"  PR #{pr['number']}: {pr['title']} (branch: {pr['headRefName']})")
    
    # Sort by PR number (newest last)
    badge_prs.sort(key=lambda x: x['number'])
    
    # If keeping latest, remove it from the list
    if args.keep_latest and badge_prs:
        latest = badge_prs.pop()
        print(f"\nKeeping latest PR #{latest['number']} open")
    
    if not badge_prs:
        print("No PRs to close.")
        return
    
    # Close PRs
    print(f"\n{'[DRY RUN] Would close' if args.dry_run else 'Closing'} {len(badge_prs)} PRs...")
    
    for pr in badge_prs:
        if args.dry_run:
            print(f"[DRY RUN] Would close PR #{pr['number']} and {'keep' if args.keep_branches else 'delete'} branch {pr['headRefName']}")
        else:
            close_pr(pr['number'], delete_branch=not args.keep_branches)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
