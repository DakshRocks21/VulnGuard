import os
import time
import requests
from github import Github
from jwt import encode
import subprocess
import dotenv

dotenv.load_dotenv()

class GitHubBot:
    def __init__(self, app_id, private_key):
        self.app_id = app_id
        self.private_key = private_key.replace("\\n", "\n")
        self.installation_id = self.get_installation_id()
        self.token = self.get_installation_access_token()

    def generate_jwt(self):
        """
        Generate a JWT for the GitHub App authentication.
        """
        now = int(time.time())
        payload = {
            "iat": now,
            "exp": now + (10 * 60),  # JWT valid for 10 minutes
            "iss": self.app_id,
        }
        return encode(payload, self.private_key, algorithm="RS256")

    def get_installation_id(self):
        """
        Get the installation ID for the GitHub App.
        """
        jwt_token = self.generate_jwt()
        url = "https://api.github.com/app/installations"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
        }
        response = requests.get(url, headers=headers).json()
        return response[0]["id"]

    def get_installation_access_token(self):
        """
        Exchange the JWT for an installation access token.
        """
        jwt_token = self.generate_jwt()
        url = f"https://api.github.com/app/installations/{self.installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
        }
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()["token"]

    def comment_on_pr(self, repo_name, pr_number, comment):
        """
        Add a comment to a pull request.
        """
        g = Github(self.token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment)
        print(f"Commented on PR #{pr_number}: {comment}")

    def get_commit_diff(self, base_sha, head_sha):
        """
        Get the git diff between two commit SHAs.
        """
        try:
            os.system("git config --global --add safe.directory /github/workspace")
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

    def get_pr_details(self, repo_name, pr_number):
        """
        Fetch PR details (title, body) via GitHub API.
        """
        try:
            url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            pr_data = response.json()
            return pr_data.get("title", ""), pr_data.get("body", "")
        except Exception as e:
            print(f"Error fetching PR details: {e}")
            return "", ""
