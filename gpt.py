import openai
import os
import subprocess
import json


class ChatGPT:
    def __init__(self, api_key, model="gpt-4"):
        """
        Initialize the ChatGPT instance with an API key and model.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.messages = []
        openai.api_key = self.api_key
    
    def set_system_prompt(self, system_prompt):
        self.messages.append({"role": "system", "content": system_prompt})
    
    def add_example(self, user_prompt, assistant_response):
        """
        Add an example interaction to the conversation.
        """
        self.messages.append({"role": "user", "content": user_prompt})
        self.messages.append({"role": "assistant", "content": assistant_response})
    
    def add_user_input(self, user_input):
        """
        Add the real user's input to the conversation.
        """
        self.messages.append({"role": "user", "content": user_input})
    
    def get_response(self, temperature=0.7, max_tokens=200):
        """
        Send the messages to the ChatGPT API and return the assistant's response.
        """
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=self.messages,
            )

            rawResponse = response.choices[0].message.content
            # Add the assistant's response to the conversation
            self.messages.append({"role": "assistant", "content": rawResponse})
            return rawResponse
        except Exception as e:
            return f"Error: {str(e)}"

class VulnGuardGPT:
    def __init__(self, openai_key):
        self.chatgpt = ChatGPT(openai_key)
        self.chatgpt.set_system_prompt("""You are a VULNERABILITY and MALWARE DETECTION expert. Analyze the code snippet and its associated GitHub commit description to ensure it: OUTPUT SHOULD BE IN JSON FORMAT WITH NO BACKTICKS. 
Performs as described: Verify the code matches the commit message.
Detects issues: Identify vulnerabilities, unintended behavior, or malicious actions, highlighting severity and providing recommendations.
Summarizes in markdown: Provide a markdown-formatted summary of the code functionality.
Highlights problems: Clearly explain any unintended or malicious actions and suggest fixes.

If vulnerabilities are found: provide a brief summary of the code functionality, the detected vulnerabilities. 

You are also given the pull request title and body, which usually contains context about the changes made.
A list of functions present in the codebase is also provided.
Based on the information provided above, come up with possible test cases/benchmarks to prove that the changes made match the title and body.
Come up with a list of functions required to recreate a minimally viable test environment for the test cases.

IMPORTANT - DO NOT DEVIATE (Output format):
{
	"summary": "Markdown-formatted summary as documented above",
	"functions": "List of functions as documented above",
    "test_cases": "Summary of the test case(s) in mind, which will be written later",
}   

OUTPUT SHOULD IN JSON FORMAT WITH NO BACKTICKS.
""")
        
    def get_response(self, user_input, max_tries=3):
        attempt = 0
        
        self.chatgpt.add_user_input(user_input)
    
        while (attempt < max_tries):
            response = self.chatgpt.get_response()
            print(attempt, response)
            
            try:
                json.loads(response)
                return response
            except json.JSONDecodeError:
                attempt += 1
                self.chatgpt.add_user_input("Not valid JSON. Please try again. NO BACKTICKS. ONLY JSON FORMAT.")
        
        return "Auto-Analysis failed. Please try again."
    
    def get_code_response(self, rag_inputs, max_tries=3, is_code_output=False):
        attempt = 0
        
        prompt = f"""Task Information:
        Write test cases based on the code. From now on, return your results only in python. Without backticks.
        ALL CODE MUST BE WRITTEN IN PYTHON, include installion of any required libraries.
        
        The Code above uses these code snippets :
        {rag_inputs}
        """
        while (attempt < max_tries):
            response = self.get_response(prompt)
            
            result = subprocess.run(
                ["python3", "-c", response],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            if not result.stderr:
                return (response,result.stdout.decode())        
            
            prompt = f"""An error occurred while running the code. Please try again.
            {result.stderr.decode()}
            
            Output only in python. Without backticks.
            """   
                
    
    def add_example(self, user_prompt, assistant_response):
        """
        Add an example interaction to the ChatGPT model.
        """
        self.chatgpt.add_example(user_prompt, assistant_response)
    
    def set_system_prompt(self, system_prompt):
        """
        Set the system prompt for the ChatGPT model.
        """
        self.chatgpt.set_system_prompt(system_prompt)
        
    def get_messages(self):
        """
        Get the messages in the ChatGPT model.
        """
        return self.chatgpt.messages
    
    def clear_messages(self):
        """
        Clear the messages in the ChatGPT model.
        """
        self.chatgpt.messages = []


# gpt = VulnGuardGPT()
# response = gpt.get_response("""Code Information:
# Title:
# "Fixed SQL injection vulnerability in login function"
# Description:
# "Fixes input validation to prevent SQL injection vulnerability in the login function."

# Function List:
# - Security.sanitize_input
# - UserService.login_user
# - UserService.change_password
# - Database.users
# - Database.execute

# Code Snippet of the changes in the pull request(with files): (do note that the code snippet is not complete)

# class Security:
#     return input_string.replace("'", "''")

# class UserService:
#     def login_user(self, username, password):
#         query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
#         if result:
#             return "Login successful"
#         else:
#             return "Invalid credentials"

#     def change_password(self, username, old_password, new_password):
#         if username not in self.db.users or self.db.users[username] != old_password:
#             return "Invalid credentials""")

# """
# {
#     “summary”: "# Analysis Results.\nThe code does not perform as described. The commit message suggests that a fix for a SQL injection vulnerability has been implemented, but the code does not show this fix. The `login_user` method in the `UserService` class still uses string formatting to include user inputs directly into the SQL query, which can lead to SQL injection attacks.\nThe only method that seems to sanitize the input is `sanitize_input` in the `Security` class. However, this method is not used anywhere in the `UserService` class or in the `Database` class which simulates database interactions.\n\n## Summary:
# The code initializes a simulated database and allows for user registration, login, and password change operations. However, it lacks sufficient input validation and escape dashing, creating a security vulnerability.\n## Highlighted Problems:
# 1. **SQL injection vulnerability** in the `login_user` function due to use of string formatting rather than parameterized queries.\n2. The `sanitize_input` method of the `Security` class is **unused**, leaving user inputs unsanitized which could lead to potential SQL injections.\n\n## Recommendations:\n1. Implement the `sanitize_input` method across all methods in the `UserService` class that interact with the database.\n2. Use **parameterized queries** instead of string formatting to compose SQL queries.",

#     “query”: "[redacted]"}"""
#     #)

# #print(gpt.get_messages())
# print(response)


# gpt = VulnGuardGPT()
# response = gpt.get_response(""" Code Information:
# Description:
# The commit message states: "Fixes input validation to prevent SQL injection vulnerability in the login function."

# Code Snippet(with files):

# main.py
# def login_user(username, password):
#    query = "SELECT * FROM users WHERE username = %s AND password = %s"
#     result = database.execute(query, (username, password,))
#     if result:
#         return "Login successful"
#     else:
#         return "Invalid credentials"
#                 """)

# print(response)