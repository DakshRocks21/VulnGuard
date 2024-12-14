from github import Github
from jwt import encode
import time
import requests
import os
import dotenv

dotenv.load_dotenv()

# GitHub App Credentials
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

def process_pull_requests():
    """
    Process pull requests and comment if 'Hello World' is found in the body.
    """
    token = get_installation_access_token()
    g = Github(token)
    repo = g.get_repo("DakshRocks21/test-me")
    pull_requests = repo.get_pulls(state="open")

    for pr in pull_requests:
        pr.create_issue_comment("Ping Pong")

if __name__ == "__main__":
    process_pull_requests()