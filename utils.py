import os
import subprocess
import requests

def get_commit_diff(base_sha, head_sha):
    """
    Get the git diff between two commit SHAs.
    """
    try:
        # Ensure the directory is considered safe
        os.system("git config --global --add safe.directory /github/workspace")
        
        # Run the git diff command
        result = subprocess.run(
            ["git", "--no-pager", "diff", f"{base_sha}..{head_sha}", "--pretty=format:%s"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit diff: {e}")
        return ""

def comment_on_pr_via_api(repo, pr_number, github_token, comment):
    """
    Comment on a GitHub pull request using the GitHub API.
    """
    try:
        response = requests.post(
            f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={"body": comment}
        )
        if response.status_code == 201:  # Status 201 indicates a successful comment creation
            print("Commented on PR successfully.")
        else:
            print(f"Error commenting on PR: {response.status_code}")
            print(response.json())
    except requests.RequestException as e:
        print(f"Error commenting on PR: {e}")
