import os
import subprocess
from github import Github

def get_commit_diff(base_sha, head_sha):
    """
    Get commit messages between two Git SHAs.
    """
    try:
        os.system("git config --global --add safe.directory /github/workspace")

        # DEBUG
        result = subprocess.run(
            ["ls", "-la"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(result.stderr)
        print(result.stdout)

        result = subprocess.run(
            ["git", "--no-pager", "log", f"{base_sha}..{head_sha}", "--pretty=format:%s"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(result.stderr)
        print(result.stdout)
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit diff: {e}")
        return ""

def comment_on_pr(pr_number, message, github_token, repo_name):
    """
    Comment on a GitHub pull request.
    """
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(message)
        print(f"Commented on PR #{pr_number}: {message}")
    except Exception as e:
        print(f"Error commenting on PR: {e}")

if __name__ == "__main__":
    # Set API URL (can be extended for use later)
    api_url = ""

    # Toggle debug mode for testing without GitHub Actions
    debug = False

    if debug:
        # Debug variables for testing locally
        base_sha = "debug_base_sha"
        head_sha = "debug_head_sha"
        github_token = "debug_github_token"
        pr_number = 1
        repo_name = "DakshRocks21/skills-review-pull-requests"
    else:
        # Get environment variables provided by GitHub Actions
        base_sha = os.getenv("BASE_SHA", "")
        head_sha = os.getenv("HEAD_SHA", "")
        github_token = os.getenv("GITHUB_TOKEN", "")
        pr_number = int(os.getenv("PR_NUMBER", 0))
        repo_name = os.getenv("GITHUB_REPOSITORY", "")
    
    try: 
        print(f"Base SHA: {base_sha[:6]}...")
    except:
        print("Base SHA not found")
    
    try:
        print(f"Head SHA: {head_sha[:6]}...")
    except:
        print("Head SHA not found")
        
    try:
        print(f"PR Number: {pr_number}")
    except:
        print("PR Number not found")
        
    try:
        print(f"Repo Name: {repo_name}")
    except:
        print("Repo Name not found")

    try:
        print(f"Github Token: {github_token}")
    except:
        print("Github Token not found")

    # Validate required environment variables
    if github_token == "":
        print("Error: Missing required environment variables.")
        exit(1)

    # Display basic debug information
    print(f"Base SHA: {base_sha[:6]}...")
    print(f"Head SHA: {head_sha[:6]}...")
    print(f"PR Number: {pr_number}")
    print(f"Repo Name: {repo_name}")

    # Get the commit difference
    commit_diff = get_commit_diff(base_sha, head_sha)
    if commit_diff:
        print(f"Commit Diff:\n{commit_diff}")
    else:
        print("No commit differences found.")

    # Add your comment logic here
    comment_message = "Done"
    comment_on_pr(pr_number, comment_message, github_token, repo_name)
