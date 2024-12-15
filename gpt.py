import openai
import os
import subprocess
import json


class ChatGPT:
    def __init__(self, api_key, model="gpt-4o"):
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

BOLD some words for emphasis key points. (e.g., **vulnerability**)

If vulnerabilities are found: provide a report of the code functionality, the detected vulnerabilities. 

You are also given the pull request title and body, which usually contains context about the changes made.
A list of functions present in the codebase is also provided.
Based on the information provided above, come up with possible test cases/benchmarks to prove that the changes made match the title and body.
The test cases should have visible and informative output that suggest the alignment of the changes with the commit message in STDOUT.
Come up with a concise list of key functions required to recreate a minimally viable test environment for the test cases.

DO NOT BE OVERLY VERBOSE.
VERY VERY IMPORTANT!!! USE MARKDOWN, BULLET POINTS, AND BACKTICKS FOR CODE. 

IMPORTANT - DO NOT DEVIATE (Output format):
{
	"summary": "Markdown-formatted summary as documented above  IN MARKDOWN FORMAT. SHOW FUNCTIONS WHICH ARE VULNERABLE. USE BULLET POINTS. USE BACKTICKS FOR CODE.",
    "report": "Detailed analysis of the code snippet, vulnerabilities, and recommendations. IN MARKDOWN FORMAT. SHOW FUNCTIONS WHICH ARE VULNERABLE. USE BULLET POINTS. USE BACKTICKS FOR CODE.",
	"functions": "Pythonic list of functions as documented above",
    "test_cases": "Summary of the test case(s) in mind, which will be written later",
}   

OUTPUT SHOULD IN JSON FORMAT WITH NO BACKTICKS AROUND IT. YOU ARE ONLY ALLOWED TO USE BACKTICKS FOR CODE INSIDE THE JSON. 
""")
#         self.add_example(r"""Code Information:
# PR Title:
# Add Login Functionality to Flask App with SQL Integration

# PR Body:
# This update enhances the simple Flask app by introducing a user login page powered by SQL. Key features include:
# User authentication using SQL database integration.
# Secure login system to protect user data.
# Updated routes and templates to support the login workflow.
# Minor adjustments to existing code for seamless integration.
# This change improves app functionality, making it suitable for applications requiring user-specific experiences or data.

# Git diff (with files):
# diff --git a/README.md b/README.md
# index 122da77..2bc41f2 100644
# --- a/README.md
# +++ b/README.md
# @@ -1 +1,14 @@
# -# test-me
# +# Secure Flask Login Application
# +
# +This Flask application is designed to provide a robust and secure login system. Below are the steps we've taken to ensure security:
# +
# +1. **Database-Driven Authentication**  
# +   User credentials are stored securely in an SQLite database, ensuring fast and reliable access.
# +
# +2. **Custom Query Building**  
# +   We've implemented dynamic query construction to allow flexibility in user input handling. This ensures our code can handle diverse authentication needs.
# +
# +3. **Detailed Logging for Testing**  
# +   The app includes detailed logging to help developers test and verify input handling, making debugging seamless.
# +
# +---
# diff --git a/app.py b/app.py
# index 7c68c7e..f52a42e 100644
# --- a/app.py
# +++ b/app.py
# @@ -1,10 +1,41 @@
# -from flask import Flask, render_template
# +from flask import Flask, request
# +import sqlite3
 
#  app = Flask(__name__)
 
# -@app.route('/')
# -def home():
# -    return render_template('index.html')
# +# Set up the database (for demonstration purposes)
# +def init_db():
# +    conn = sqlite3.connect('example.db')
# +    cursor = conn.cursor()
# +    cursor.execute('''
# +        CREATE TABLE IF NOT EXISTS users (
# +            id INTEGER PRIMARY KEY AUTOINCREMENT,
# +            username TEXT,
# +            password TEXT
# +        )
# +    ''')
# +    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
# +    conn.commit()
# +    conn.close()
# +
# +@app.route('/login', methods=['GET', 'POST'])
# +def login():
# +    username = request.args.get('username')
# +    password = request.args.get('password')
# +
# +    conn = sqlite3.connect('example.db')
# +    cursor = conn.cursor()
# +
# +    # Intentionally vulnerable query (DO NOT use in production)
# +    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
# +    cursor.execute(query)
# +    user = cursor.fetchone()
# +
# +    if user:
# +        return f"Welcome, {user[1]}!"
# +    else:
# +        return "Invalid username or password."
 
#  if __name__ == '__main__':
# +    init_db()
#      app.run(debug=True)
# diff --git a/static/style.css b/static/style.css
# index 7a140c7..2afc7ff 100644
# --- a/static/style.css
# +++ b/static/style.css
# @@ -1,10 +1,85 @@
# -body {
# -    font-family: Arial, sans-serif;
# +/* Reset some basic styles */
# +body, html {
#      margin: 0;
# -    padding: 20px;
# +    padding: 0;
# +    font-family: Arial, sans-serif;
#      background-color: #f4f4f4;
# +    color: #333;
# +}
# +
# +/* Center the content */
# +.container {
# +    max-width: 400px;
# +    margin: 50px auto;
# +    padding: 20px;
# +    background: #fff;
# +    border-radius: 8px;
# +    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
# +    text-align: center;
#  }
 
# +/* Style the heading */
#  h1 {
# +    font-size: 24px;
# +    margin-bottom: 10px;
#      color: #333;
#  }
# +
# +/* Add spacing to the description */
# +p {
# +    font-size: 14px;
# +    color: #666;
# +    margin-bottom: 20px;
# +}
# +
# +/* Style the form */
# +form {
# +    display: flex;
# +    flex-direction: column;
# +    gap: 15px;
# +}
# +
# +.form-group {
# +    text-align: left;
# +}
# +
# +/* Style the labels */
# +label {
# +    font-size: 14px;
# +    font-weight: bold;
# +    margin-bottom: 5px;
# +    display: block;
# +}
# +
# +/* Style the input fields */
# +input[type="text"],
# +input[type="password"] {
# +    width: 100%;
# +    padding: 10px;
# +    font-size: 14px;
# +    border: 1px solid #ccc;
# +    border-radius: 4px;
# +    outline: none;
# +}
# +
# +input[type="text"]:focus,
# +input[type="password"]:focus {
# +    border-color: #007BFF;
# +    box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
# +}
# +
# +/* Style the button */
# +button {
# +    padding: 10px;
# +    font-size: 16px;
# +    color: #fff;
# +    background-color: #007BFF;
# +    border: none;
# +    border-radius: 4px;
# +    cursor: pointer;
# +    transition: background-color 0.3s ease;
# +}
# +
# +button:hover {
# +    background-color: #0056b3;
# +}
# diff --git a/templates/index.html b/templates/index.html
# index 7c922b0..d506a17 100644
# --- a/templates/index.html
# +++ b/templates/index.html
# @@ -1,13 +1,29 @@
#  <!DOCTYPE html>
#  <html lang="en">
# +
#  <head>
#      <meta charset="UTF-8">
#      <meta name="viewport" content="width=device-width, initial-scale=1.0">
# -    <title>Flask App</title>
# +    <title>Secure Login Portal</title>
#      <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
#  </head>
# +
#  <body>
# -    <h1>Welcome to Flask!</h1>
# -    <p>This is a simple Flask application.</p>
# +    <div class="container">
# +        <h1>Login</h1>
# +        <p>Welcome to the secure login portal. Please enter your credentials below.</p>
# +        <form action="/login" method="get">
# +            <div class="form-group">
# +                <label for="username">Username</label>
# +                <input type="text" id="username" name="username" placeholder="Enter your username" required>
# +            </div>
# +            <div class="form-group">
# +                <label for="password">Password</label>
# +                <input type="password" id="password" name="password" placeholder="Enter your password" required>
# +            </div>
# +            <button type="submit">Login</button>
# +        </form>
# +    </div>
#  </body>
# -</html>
# +
# +</html>
# \ No newline at end of file""", """{
#     "summary": "### Summary of the Code Changes\n\nThis update introduces a secure login functionality to a Flask application, with integration to an SQLite database for user authentication. Key changes include:\n\n- **Flask Route Implementation:**\n  - A new `/login` route has been added to handle GET and POST requests for user login functionality.\n  - `app.py:16-37`\n\n- **Database Initialization:**\n  - A function `init_db` creates a SQLite database and a `users` table if it doesn't already exist.\n  - Preloads the database with a default user (`admin`, `admin123`).\n  - `app.py:8-14`\n\n- **Dynamic Query Construction:**\n  - Queries are dynamically constructed using string interpolation, leading to a potential SQL injection vulnerability.\n  - `app.py:28`\n\n- **Frontend Updates:**\n  - A login form is added to the HTML template to accept user credentials.\n  - Enhanced CSS styling for improved user experience.\n  - `templates/index.html:9-28`\n  - `static/style.css:5-84`\n",
#     "report": "### Detailed Vulnerability Analysis\n\n#### File: `app.py`\n\n1. **Dynamic Query Construction (`app.py:28`):**\n   - The query to fetch user details is constructed using Python string interpolation:\n     ```python\n     query = f\"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'\"\n     ```\n   - **Vulnerability:** This approach is susceptible to SQL injection attacks, where an attacker could inject malicious SQL commands through the `username` or `password` fields.\n   - **Severity:** High\n   - **Recommendation:** Use parameterized queries to prevent SQL injection. Replace the above code with:\n     ```python\n     query = \"SELECT * FROM users WHERE username = ? AND password = ?\"\n     cursor.execute(query, (username, password))\n     ```\n\n2. **Hardcoded Credentials in Database Initialization (`app.py:13`):**\n   - The default `admin` user credentials are hardcoded into the application.\n   - **Risk:** This is not suitable for production environments as it exposes the application to unauthorized access if the database is compromised.\n   - **Recommendation:** Use environment variables or a secure secrets manager to initialize sensitive credentials.\n\n#### File: `static/style.css`\n\n- **Style Enhancements (`static/style.css:5-84`):**\n  - Improves user experience but does not directly impact functionality or security.\n\n#### File: `templates/index.html`\n\n- **Frontend Form (`templates/index.html:9-28`):**\n  - Collects user credentials through a form and sends them using the GET method, embedding sensitive data in the URL.\n  - **Risk:** GET requests expose sensitive information in server logs and browser history.\n  - **Recommendation:** Use POST requests for transmitting sensitive data.\n\n### Recommendations\n\n- Refactor the SQL queries to use parameterized queries.\n- Avoid hardcoding sensitive credentials; use environment variables instead.\n- Update the form to use the POST method for submitting credentials.\n\n### Additional Observations\n\n- Logging is not implemented for failed or successful login attempts. Logging can help identify suspicious activities.\n- Input sanitization and validation are missing for the username and password fields.\n",
#     "functions": [
#         "init_db",
#         "login"
#     ],
#     "test_cases": "### Test Cases for Validation\n\n1. **Successful Login Test:**\n   - Input: Valid `username` and `password` (e.g., `admin`, `admin123`).\n   - Expected Output: Displays a welcome message.\n\n2. **Invalid Login Test:**\n   - Input: Invalid `username` and/or `password`.\n   - Expected Output: Displays an 'Invalid username or password' message.\n\n3. **SQL Injection Test:**\n   - Input: Malicious payload in `username` or `password` (e.g., `admin' OR '1'='1`).\n   - Expected Output: Prevent SQL injection and display an error message.\n\n4. **GET vs POST Test:**\n   - Test login form behavior with GET and POST methods.\n   - Expected Output: Only POST requests should be accepted.\n\n5. **Database Initialization Test:**\n   - Validate that the database initializes correctly with the default user.\n\n6. **Frontend Validation Test:**\n   - Test if the form fields enforce required input.\n",
#     "test_environment": "### Minimal Test Environment Setup\n\n- **Dependencies:**\n  ```python\n  pip install flask sqlite3\n  ```\n\n- **Environment Setup:**\n  - Create a new SQLite database (`example.db`).\n  - Initialize the database using the `init_db` function.\n\n- **Functions to Implement for Tests:**\n  - `test_successful_login`\n  - `test_invalid_login`\n  - `test_sql_injection`\n  - `test_form_method`\n  - `test_db_initialization`\n  - `test_frontend_validation`\n"
# }
# """)
        
    def get_response(self, user_input, max_tries=3):
        attempt = 0
        
        self.chatgpt.add_user_input(user_input)
    
        while (attempt < max_tries):
            response = self.chatgpt.get_response() 
            try:
                json.loads(response)
                return response
            except json.JSONDecodeError:
                attempt += 1
                self.chatgpt.add_user_input("Not valid JSON. Please try again. NO BACKTICKS. ONLY JSON FORMAT.")
        
        print(response)
        return "Auto-Analysis failed. Please try again."
    
    def get_code_response(self, rag_inputs, max_tries=3, is_code_output=False):
        attempt = 0
        
        prompt = f"""Task Information:
Write test cases based on the code. Output your response in JSON format like the following:
{{"code": "import sys\nsys.exit(0)"}}

The test case should recreate the environment from scratch, assuming that nothing is present.

The Code above uses these code snippets :
{rag_inputs}"""

        while (attempt < max_tries):
            response = json.loads(self.get_response(prompt))  # TODO: Implement error handling
            
            result = subprocess.run(
                ["python", "-c", response],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            if not result.stderr:
                return (response, result.stdout.decode())        
            
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