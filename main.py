import os
import requests
from github import Github
from utils import get_commit_diff, comment_on_pr_via_api

def main():
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

    # Fetch pull request details
    try:
        pr_data = requests.get(
            f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json"
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

    # Placeholder comment message
    comment_message = "This is an automated review comment. Details:\n\n" + prompt

    # Comment on the pull request
    comment_on_pr_via_api(repo_name, pr_number, github_token, comment_message)

if __name__ == "__main__":
    main()
