import os
import subprocess
import requests
from github import Github

def get_commit_diff(base_sha, head_sha):
    try:
        result = subprocess.check_output(
            ["git", "log", f"{base_sha}..{head_sha}", "--pretty=format:%s"],
            text=True,
        )
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit diff: {e}")
        return ""

def send_to_api(commit_diff, api_url):
    payload = {"commits": commit_diff}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        print(f"API response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to API: {e}")

def comment_on_pr(pr_number, message, github_token, repo_name):
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)

if __name__ == "__main__":
    api_url = ""
    debug = True
    if debug:
        os.environ["BASE_SHA"] = "123456"
        os.environ["HEAD_SHA"] = "abcdef"
        os.environ["GITHUB_TOKEN"] = ""
        os.environ["PR_NUMBER"] = "1"
        os.environ["GITHUB_REPOSITORY"] = "DakshRocks21/skills-review-pull-requests"
        
    else:
        base_sha = os.environ["BASE_SHA"]
        head_sha = os.environ["HEAD_SHA"]
        
        github_token = os.environ["GITHUB_TOKEN"]
        pr_number = int(os.environ["PR_NUMBER"])
        repo_name = os.environ["GITHUB_REPOSITORY"]

    commit_diff = get_commit_diff(base_sha, head_sha)

    send_to_api(commit_diff, api_url)
    
    comment_on_pr(pr_number, "Done", github_token, repo_name)
