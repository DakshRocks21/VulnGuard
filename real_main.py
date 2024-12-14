import os
import dotenv
from GitHubBot import GitHubBot

dotenv.load_dotenv()

APP_ID = 1087519
PRIVATE_KEY = os.getenv("BOT_KEY")

# Initialize the bot
bot = GitHubBot(APP_ID, PRIVATE_KEY)

# Retrieve environment variables
base_sha = os.getenv("BASE_SHA", "")
head_sha = os.getenv("HEAD_SHA", "")
pr_number = int(os.getenv("PR_NUMBER", 0)) + 1
repo_name = os.getenv("GITHUB_REPOSITORY", "")
openai_key = os.getenv("OPENAI_API_KEY", "")

# Validate required environment variables
if not all([base_sha, head_sha, repo_name, openai_key]):
    print("Error: Missing required environment variables.")
    exit(1)

# Get PR details
title, body = bot.get_pr_details(repo_name, pr_number)

# Get the git diff
commit_diff = bot.get_commit_diff(base_sha, head_sha)

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

# Comment on the pull request
comment_message = f"This is an automated review comment. Details:\n\n{prompt}"
bot.comment_on_pr(repo_name, pr_number, comment_message)