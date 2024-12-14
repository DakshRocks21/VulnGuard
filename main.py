import os
import subprocess
from gpt import VulnGuardGPT
from github import Github

def get_commit_diff(base_sha, head_sha):
    """
    Get commit messages between two Git SHAs.
    """
    try:
        os.system("git config --global --add safe.directory /github/workspace")

        result = subprocess.run(
            ["git", "--no-pager", "diff", f"{base_sha}..{head_sha}", "--pretty=format:%s"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(result.stderr)
        print(result.stdout)
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit diff: {e}")
        return ""

def comment_on_pr(pr_number, message, pr):
    """
    Comment on a GitHub pull request.
    """
    try:
        pr.create_issue_comment(message)
        print(f"Commented on PR #{pr_number}: {message}")
    except Exception as e:
        print(f"Error commenting on PR: {e}")

if __name__ == "__main__":
    # Get environment variables provided by GitHub Actions
    base_sha = os.getenv("BASE_SHA", "")
    head_sha = os.getenv("HEAD_SHA", "")
    github_token = os.getenv("GITHUB_TOKEN", "")
    pr_number = int(os.getenv("PR_NUMBER", 0)) + 1
    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Validate required environment variables
    if github_token == "" or openai_key == "":
        print("Error: Missing required environment variables (GITHUB_TOKEN or OPENAI_API_KEY).")
        exit(1)

    g = Github(github_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    # Get the commit difference
    commit_diff = get_commit_diff(base_sha, head_sha)

    gpt = VulnGuardGPT()
    prompt = f"""Code Information:
Description:
{pr.get_comment(0)}

Git diff (with files):
{commit_diff}
"""
    print(prompt)
# response = gpt.get_response(prompt)

    # Add your comment logic here
    # comment_message = "Done"
    # comment_on_pr(pr_number, comment_message, pr)
