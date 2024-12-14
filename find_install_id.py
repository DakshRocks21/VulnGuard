import requests
from jwt import encode
import time
import os
import dotenv

dotenv.load_dotenv()

APP_ID = 1087519
bot_key = os.getenv("BOT_KEY", "").replace("\\n", "\n")


def generate_jwt(bot_key):
    """
    Generate a JWT for the GitHub App authentication.
    """
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + (10 * 60),  # JWT valid for 10 minutes
        "iss": APP_ID,
    }
    return encode(payload, bot_key, algorithm="RS256")

def get_installation_id(bot_key):
    """
    Get the installation ID for the GitHub App.
    """
    jwt_token = generate_jwt(bot_key)
    url = f"https://api.github.com/app/installations"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers).json()
    print(response)

print(get_installation_id(bot_key))