import os
import subprocess
import requests
from jwt import encode
import time
from github import Github

APP_ID = 1087519


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

def get_pr_details(repo_name, pr_number, github_token):
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
    return title, body

def comment_on_pr_via_api(bot_key, repo, pr_number, comment):
    """
    Comment on a GitHub pull request using the GitHub API.
    """
    try:
        INSTALLATION_ID = get_installation_id(bot_key, repo)["installation_id"]
        token = get_installation_access_token(bot_key, INSTALLATION_ID)
        
        g = Github(token)
        repo = g.get_repo(repo)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment)
        
        print(f"Commented on PR #{pr_number}")
    except requests.RequestException as e:
        print(f"Error commenting on PR: {e}")


def generate_jwt(bot_key):
    """
    Generate a JWT for the GitHub App authentication.
    """
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + (10 * 60),  # JWT valid for 10 minutes
        "iss": APP_ID,
    }
    return encode(payload, bot_key, algorithm="RS256")

def get_installation_access_token(jwt_token, installation_id):
    """
    Exchange the JWT for an installation access token.
    """
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["token"]


def get_installation_id(bot_key, repo_name):
    """
    Find the installation ID and user for the given repository name.
    """
    # Fetch all installations of the app
    jwt_token = generate_jwt(bot_key)
    url = f"https://api.github.com/app/installations"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    installations = requests.get(url, headers=headers).json()

    # Loop through installations and check repositories
    for installation in installations:
        installation_id = installation["id"]
        account_login = installation["account"]["login"]

        # Get repositories for this installation
        token = get_installation_access_token(jwt_token, installation_id)
        repo_url = "https://api.github.com/installation/repositories"
        repo_headers = {
            "Authorization": f"Bearer {token}", 
            "Accept": "application/vnd.github+json",
        }
        repo_response = requests.get(repo_url, headers=repo_headers)
        repo_response.raise_for_status()
        repositories = repo_response.json()["repositories"]

        # Check if the repository matches
        for repo in repositories:
            if repo["full_name"] == repo_name:
                return {
                    "installation_id": installation_id,
                    "added_by": account_login,
                    "repo_name": repo_name,
                }

    raise ValueError(f"Repository '{repo_name}' not found in any installation.")