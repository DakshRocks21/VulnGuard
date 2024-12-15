import os
from utils import get_commit_diff, comment_on_pr_via_api, get_pr_details
from gpt import VulnGuardGPT
from parser import CodeParser

def main():
    # Retrieve environment variables
    base_sha = os.getenv("BASE_SHA", "")
    head_sha = os.getenv("HEAD_SHA", "")
    github_token = os.getenv("GITHUB_TOKEN", "")
    pr_number = int(os.getenv("PR_NUMBER", 0)) + 1
    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    bot_key = os.getenv("BOT_KEY", "").replace("\\n", "\n")

    # Validate required environment variables
    if github_token == "" or openai_key == "" or bot_key == "":
        print("Error: Missing required environment variables.")
        exit(1)    

    # Get the git diff
    commit_diff = get_commit_diff(base_sha, head_sha)
    
    title, body = get_pr_details(repo_name, pr_number, github_token)

    # Extract all the symbols
    parser = CodeParser()
    symbols = '\n'.join(parser.parse())

    # Construct GPT prompt
    prompt = f"""Code Information:
PR Title:
{title}

PR Body:
{body}

Function List:
{symbols}

Git diff (with files):
{commit_diff}
"""
    
    gpt = VulnGuardGPT(openai_key)
    response = gpt.get_response(prompt)
    
    #print(response)
    
    # Comment on the pull request
    comment_on_pr_via_api(bot_key, repo_name, pr_number, response)

if __name__ == "__main__":
    main()
