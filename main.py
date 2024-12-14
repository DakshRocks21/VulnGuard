import os
import subprocess
import requests
from github import Github

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

def comment_on_pr_via_api(pr, comment):
    """
    Comment on a GitHub pull request using the GitHub API.
    """
    try:
        pr.create_issue_comment(comment)
        print("Commented on PR successfully.")
    except requests.RequestException as e:
        print(f"Error commenting on PR: {e}")

if __name__ == "__main__":
    # Retrieve environment variables
    base_sha = os.getenv("BASE_SHA", "")
    head_sha = os.getenv("HEAD_SHA", "")
    github_token = os.getenv("GITHUB_TOKEN", "")
    pr_number = int(os.getenv("PR_NUMBER", 0)) + 1
    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Validate required environment variables
    if not all([base_sha, head_sha, github_token, repo_name, openai_key]):
        print("Error: Missing required environment variables.")
        exit(1)

    # Initialize GitHub repository object
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    # Get PR details via GitHub API
    try:
        pr_data = requests.get(
            f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json"
            }
        ).json()
        
        title = pr_data.get("title", "")
        body = pr_data.get("body", "")
    except Exception as e:
        print(f"Error fetching PR details: {e}")
        exit(1)

    # Get the git diff
    commit_diff = get_commit_diff(base_sha, head_sha)

    # Construct GPT prompt
    prompt = f"""Code Information:
PR Title:
{title}

PR Body:
{body}

Git diff (with files):
{commit_diff}
"""
    print("Generated GPT prompt:")
    print(prompt)

    # Here you can integrate with VulnGuardGPT
    # For now, we'll create a placeholder comment
    comment_message = "This is an automated review comment. Details:\n\n" + prompt

    # Comment on the pull request using the API
    comment_on_pr_via_api(pr, comment_message)
