import os
import subprocess
import requests
from jwt import encode
import time
import dotenv
from github import Github

dotenv.load_dotenv()

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
        token = get_installation_access_token()
        g = Github(token)
        repo = g.get_repo(repo)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment)
        print(f"Commented on PR #{pr_number}")
    except requests.RequestException as e:
        print(f"Error commenting on PR: {e}")

APP_ID = 1087519
PRIVATE_KEY = os.getenv("BOT_KEY").replace("\\n", "\n")

def generate_jwt():
    """
    Generate a JWT for the GitHub App authentication.
    """
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + (10 * 60),  # JWT valid for 10 minutes
        "iss": APP_ID,
    }
    return encode(payload, PRIVATE_KEY, algorithm="RS256")

def get_installation_id():
    """
    Get the installation ID for the GitHub App.
    """
    jwt_token = generate_jwt()
    url = f"https://api.github.com/app/installations"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers).json()
    print("Installation ID:", response[0]["id"])
    return response[0]["id"]
    
INSTALLATION_ID = get_installation_id()

def get_installation_access_token():
    """
    Exchange the JWT for an installation access token.
    """
    jwt_token = generate_jwt()
    url = f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["token"]