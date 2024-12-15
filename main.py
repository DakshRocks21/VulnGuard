import json
import os

from utils import get_commit_diff, comment_on_pr_via_api, get_pr_details
from gpt import VulnGuardGPT
from parser import CodeParser
from coderag import CodeRAG

def main():
    # Retrieve environment variables
    base_sha = os.getenv("BASE_SHA", "")
    head_sha = os.getenv("HEAD_SHA", "")
    github_token = os.getenv("GITHUB_TOKEN", "")
    pr_number = int(os.getenv("PR_NUMBER", 0))
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
    response = json.loads(gpt.get_response(prompt))

    # Comment on the pull request
    comment_on_pr_via_api(bot_key, repo_name, pr_number, json.dumps(response))

    # Generate test cases
    functions = response['functions']
    rag = CodeRAG()
    rag_query = rag.query(functions)

    rag_response = gpt.get_code_response(rag_query)
    if type(rag_response) == tuple:
        response['script'] = rag_response[0]
        response['output'] = rag_response[1]
    else:
        response['script'] = "# No script created"
        response['output'] = "No output generated"
    
    comment_on_pr_via_api(bot_key, repo_name, pr_number, json.dumps(response), is_script=True)

if __name__ == "__main__":
    main()
