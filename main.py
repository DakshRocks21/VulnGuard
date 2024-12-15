import json
import os
import base64

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
    bot_key = "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcEFJQkFBS0NBUUVBMng1ZEczN0xaZ0NxRkxiZ0tTWnRQZXpLK1dyY0N2U1NMV1Vxb1JWcENIRVV2V1lOCndKTVRSdUdFQVI1WTZldTJ2NjBMRStmZWo1dHBSa09NWXhiOHVPK3JXWEdtNzU2dldIYlNkTlowUS9XMm41WHEKTlRhV2pDTFRmZDc4SXpUZit6UkNNbnRGeVVHMk95aExqZkVPTS8wVEZsY25CeWhYTWh0TjJreTVvVlJJWUM3WgptNlg2R2pUY3ZRK0tjeXZVWnV2aEFVa1JnVFBXMWFxb1hJeHdSbHIrUXZZa2VEWUx2eldzOW5sL0N1QzgvbG1GCkdMVnVBQndRRklmdU04S2w5ckdTeER4V3dUNHZBN0dRa2FyL2IyUVlQQkNUc3g5ZzRvL3pOMkNQSzNGWm54Z1YKNmYxSkRlRDhiUjQ5YkRXYU9aNktiQkhzbDhRK3dKeGFzRUgvbVFJREFRQUJBb0lCQVFDQUxJTEtVcUVvU2Jzego0c1c5VEgwYWZDay9QUUw2WlpZY2Q5RTM2UTVIb2Q0LzdES2ZNMmxUVFJlcWo5WHkvNjhtOEZKS2twZmQ2VXJyCmp4ZlAzdUoyUzd3djFndVFuNEp5ZlE4ZXlWTzViVUltbDhzbzFZVzY4NlJEUE96QXEyMVp4SGYwajZlQzBxMkcKYlV2RSsvMFM3RGIrR256NTh0OE9zR29hQ0VlTjFtbklFZUs2K21SNTNMbmdRSDVGWnN2TlVuTU1tVklvSGFIeQpZSGNGOW5EaXFjczZYMC9zMU5LVWVKZnQrTUpZREEvQ1NTSHRoOU9KU0lLMkhsY1crZXBYYnh6dlhWSWlUMVJPCkFTK2ppRkVFbUxPbk9XTlNDU3pZWW1BczVITkw5WWRMbXFkNHB1MGQ5SGd2TjVaQ0JIOThZWGhCQkwzTnRoVjcKa0d0TFA0c0JBb0dCQVAxZTJZYVB0elhnSHVoR1RVQVplUU44S0RRaGhuNmlVZnVTUlE1aGJOc1BTUjlydnV4aAprSmlRUWdOZ05VdGFjWGE3L1BtOUJldGVzelRvY3dUblFsM3ZJbHlESlBvZ2F5dER3R2RGcUxmL1JSL1VMa3NlCjZqQ0FCM1F0NG9yU1JHNXhIOFFCcEVobkJnUzdUMEtpZDF4Um1OeHNiaTdBNThGQmphc2pPd0VYQW9HQkFOMWsKZzU5Mko5TkRldVgwQk1INkpUMGZqcTJGZ0IvbFpyUkR6dU03eUFnRExjVmlRZFcxMERFWFh4REJVZnVYSDRRaQpKRkRlbkxMUFlSVk9EU0ZiV0lhOUJvZEFzOFhFRXNHOHpvOHgvaFRyeUVPZi8wWmRvaTJZdFd1ei9FNWpsbHBLCllLL05VNTh0UVdRQ3NRYk1JUFRSbEJLaE5YeFR2S0VRaWwyOG01TFBBb0dCQUl3aEowRnF2ck5IVHhDN3dRSFEKbE1NK3FhV2JYUjB3ZlJNYjVLRjlkSXo3T1QvdGdWeU80VC9mbVFMdzlNakdMcmF5WmNsaHA2SnpiNzIxU2RmTwpaMEE0ZjlLV25aN1F5elRVZGRjb0NaWXAwbnMyQ0p4M2JxS0FUSjhPdVpwNWpHdGdtV2I0V1huSnNPUnhDL2NZCmo5YzVNY2ZIR0hFM00zWUk0V2RqUnNEbEFvR0FCbHhyOTdueVhQeVVYR1VOZWZGUS9wZVlodDNPRjV5RXZlc3cKMTVDUko4SEhuK001MXdVWlRUL0pxSGFWZjNBUkpML0NZVngwRGlNdE8rcDVNQnNxeVB4SFlyMTJMTmw4WEhxcgpTS3Y4QytmV1lqTUhwNkxyRlBwTlJDSHd2dVBYbnhLQ0Fxc1ltdnMyNU1PN0NHSDNGSEd0R25mdFRId3ZjRVZFClpIc1YwVHNDZ1lCbXVoS25RbkJZWXJiczVUcjV4clU5OGRkYU4rMmFjZkxFelhrd2hReFJBSXZGT2xVcDJ0YVAKNnlBT2lLOHV4YlFVZ0FUWVZlTEhuQ1pBVTFOZXZFdy9JSWp1Umpuc1NubnN5RUI4TnczSzZrendKSWtvZE5hUAptdXZ1Z2hhUERGaWwxdElvdUVDZkJ1VWtnRGFJczVhOG5RU3BCYnY4L1NVaGlrSUFMUWY2eUE9PQotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQ=="
    bot_key = base64.b64decode(bot_key).decode("utf-8")

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
