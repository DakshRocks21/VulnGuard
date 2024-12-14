import os
import subprocess
import requests
import json
from github import Github, PullRequest
from gpt import VulnGuardGPT
from coderag import CodeRAG

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
        response = requests.post(
            f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
            headers={
                "Authorization": f"Bearer {os.getenv('GITHUB_USER_TOKEN', '')}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={"body": comment}
        )
        if response.status_code == 200:
            print("Commented on PR successfully.")
        else:
            print(response.status_code)
            print(response.json())
            print("Error commenting on PR.")
    except requests.RequestException as e:
        print(f"Error commenting on PR: {e}")

if __name__ == "__main__":
    # # Retrieve environment variables
    # base_sha = os.getenv("BASE_SHA", "")
    # head_sha = os.getenv("HEAD_SHA", "")
    # github_token = os.getenv("GITHUB_TOKEN", "")
    # pr_number = int(os.getenv("PR_NUMBER", 0)) + 1
    # repo_name = os.getenv("GITHUB_REPOSITORY", "")
    # openai_key = os.getenv("OPENAI_API_KEY", "")

    # # Validate required environment variables
    # if not all([base_sha, head_sha, github_token, repo_name, openai_key]):
    #     print("Error: Missing required environment variables.")
    #     exit(1)

    # # Initialize GitHub repository object
    # g = Github(github_token)
    # repo = g.get_repo(repo_name)
    # pr = repo.get_pull(pr_number)

    # # Get PR details via GitHub API
    # try:
    #     pr_data = requests.get(
    #         f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}",
    #         headers={
    #             "Authorization": f"Bearer {github_token}",
    #             "Accept": "application/vnd.github.v3+json"
    #         }
    #     ).json()
    #     
    #     title = pr_data.get("title", "")
    #     body = pr_data.get("body", "")
    # except Exception as e:
    #     print(f"Error fetching PR details: {e}")
    #     exit(1)

    # # Get the git diff
    # commit_diff = get_commit_diff(base_sha, head_sha)

    title = "Data now comes from credential file"
    body = "Change it so that password is not hardcoded"

    commit_diff = r"""diff --git a/backend/client.py b/backend/client.py
index 0f62ff9..3451c85 100644
--- a/backend/client.py
+++ b/backend/client.py
@@ -39,7 +39,21 @@ image_debug = args.image_debug
 server_ip = args.ip
 server_port = args.port

-password = "YW1vZ3Vz"
+# Read credentials
+cred_path = os.path.join(os.path.dirname(__file__), "../misc/credentials.txt")
+credentials = {}
+
+with open(cred_path, "r") as f:
+    for line in f:
+       (key, val) = line.split("=")
+       credentials[key] = val
+    f.close()
+
+try:
+    password = credentials["password"].strip("\n")
+except KeyError:
+    print("[FATAL] Password not found in credentials.txt")
+    sys.exit(1)

 W, H = 640, 640   # Width and height of cut image

diff --git a/backend/server.py b/backend/server.py
index e6241ec..8b1ceed 100644
--- a/backend/server.py
+++ b/backend/server.py
@@ -10,6 +10,7 @@ import socket
 import argparse
 import os
 import time
+import sys

 import requests

@@ -29,8 +30,23 @@ server_port = args.port

 url = args.url

-auth_key = os.environ["QUEUE_AUTH_KEY"]
-auth_token = os.environ["QUEUE_AUTH_TOKEN"]
+# Read Credentials
+cred_path = os.path.join(os.path.dirname(__file__), "../misc/credentials.txt")
+credentials = {}
+
+with open(cred_path, "r") as f:
+    for line in f:
+       (key, val) = line.split("=")
+       credentials[key] = val
+    f.close()
+
+try:
+    password = credentials["password"].strip("\n")
+    auth_key = credentials["auth_key"].strip("\n")
+    auth_token = credentials["auth_token"].strip("\n")
+except KeyError:
+    print("[FATAL] Missing credentials in credentials.txt")
+    sys.exit(1)

 stall_name = ["Drinks", "Snacks", "Malay 1", "Malay 2", "Western", "Chicken Rice", "Oriental Taste", "CLOSED"]
 displayed = {}  # Format: [<Tkinter Label Class>, <Last Updated Time (int)>]
@@ -38,8 +54,6 @@ max_clients = 8

 last_update_threshold = 60

-password = "YW1vZ3Vz"
-
 # Debug print
 def debug_print(msg):
     if debug:
diff --git a/misc/credentials.txt b/misc/credentials.txt
new file mode 100644
index 0000000..6188cf8
--- /dev/null
+++ b/misc/credentials.txt
@@ -0,0 +1,3 @@
+password=REDACTED
+auth_key=REDACTED
+auth_token=REDACTED
\ No newline at end of file
diff --git a/tools/get_coords_from_image.py b/misc/get_coords_from_image.py
similarity index 100%
rename from tools/get_coords_from_image.py
rename to misc/get_coords_from_image.py
"""

    function_list = """click_event
last_update_checker
index
update_timing
get_timing
debug_print
init_GUI
additem
last_update_updater
on_recv_data
main
Queue
__init__
cutImage
countPeople
getQueueTime
debug_print
handle_queue
main
additem
Arrow
__init__
Block
__init__
HuskyLensLibrary
__init__
writeToHuskyLens
calculateChecksum
cmdToBytes
splitCommandToParts
getBlockOrArrowCommand
processReturnData
convert_to_class_object
knock
learn
forget
setCustomName
customText
clearText
requestAll
saveModelToSDCard
loadModelFromSDCard
savePictureToSDCard
saveScreenshotToSDCard
blocks
arrows
learned
learnedBlocks
learnedArrows
getObjectByID
getBlocksByID
getArrowsByID
algorthim
count
learnedObjCount
frameNumber"""

    # Construct GPT prompt
    prompt = f"""Code Information:
PR Title:
{title}

PR Body:
{body}

Function List:
{function_list}

Git diff (with files):
{commit_diff}
"""
    print("Generated GPT prompt:")
    print(prompt)

    gpt = VulnGuardGPT()
    response = json.loads(gpt.get_response(prompt))  # TODO: Implement error handling

    print("GPT response:")
    print(response)

    rag = CodeRAG()
    query = rag.query(response["functions"])

    response = gpt.get_code_response(query, max_tries=1)
    if type(response) == tuple:
        response, result = response
        print(response)
        print(result)

    # Here you can integrate with VulnGuardGPT
    # For now, we'll create a placeholder comment
    comment_message = "This is an automated review comment. Details:\n\n" + prompt

    # Comment on the pull request using the API
    # comment_on_pr_via_api(repo_name, pr_number, github_token, comment_message)
