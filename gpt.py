import openai
import os
import dotenv
import re
import subprocess

dotenv.load_dotenv()

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
    def __init__(self, chatgpt=ChatGPT(api_key=os.getenv("OPENAI_API_KEY"))):
        self.chatgpt = chatgpt
        self.chatgpt.set_system_prompt("""
You are a VULNERABILITY and MALWARE DETECTION expert. Analyze the code snippet and its associated GitHub commit description to ensure it:
Performs as described: Verify the code matches the commit message.
Detects issues: Identify vulnerabilities, unintended behavior, or malicious actions, highlighting severity and recommendations.
Summarizes in markdown: Provide a markdown-formatted summary of the code functionality.
Highlights problems: Clearly explain any unintended or malicious actions and suggest fixes.
Be SHORT and CONCISE, and provide actionable feedback.

IF there are NO vulnerabilities:
If no vulnerabilities are found, provide a brief summary of the code functionality. Do not do a deep analysis in responses. BE CONCISE.

Do provide a short recommendation if any, regardless of the presence of vulnerabilities.

Formatting Rules:
Use single backticks for inline code. Use <code> tags for multiline code. Keep explanations concise and actionable.""")
        
    def get_response(self, user_input):
        
        self.chatgpt.add_user_input(user_input)
        response = self.chatgpt.get_response()
        
        return response
    
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
# response = gpt.get_response(""" Code Information:
# Description:
# The commit message states: "Fixes input validation to prevent SQL injection vulnerability in the login function."

# Code Snippet(with files):

# main.py
# def login_user(username, password):
#     query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
#     result = database.execute(query)
#     if result:
#         return "Login successful"
#     else:
#         return "Invalid credentials"
#                 """)

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