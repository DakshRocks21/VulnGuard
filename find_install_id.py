import requests
from jwt import encode
import time
import os
import dotenv

dotenv.load_dotenv()

APP_ID = 1087519
bot_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA2x5dG37LZgCqFLbgKSZtPezK+WrcCvSSLWUqoRVpCHEUvWYN
wJMTRuGEAR5Y6eu2v60LE+fej5tpRkOMYxb8uO+rWXGm756vWHbSdNZ0Q/W2n5Xq
NTaWjCLTfd78IzTf+zRCMntFyUG2OyhLjfEOM/0TFlcnByhXMhtN2ky5oVRIYC7Z
m6X6GjTcvQ+KcyvUZuvhAUkRgTPW1aqoXIxwRlr+QvYkeDYLvzWs9nl/CuC8/lmF
GLVuABwQFIfuM8Kl9rGSxDxWwT4vA7GQkar/b2QYPBCTsx9g4o/zN2CPK3FZnxgV
6f1JDeD8bR49bDWaOZ6KbBHsl8Q+wJxasEH/mQIDAQABAoIBAQCALILKUqEoSbsz
4sW9TH0afCk/PQL6ZZYcd9E36Q5Hod4/7DKfM2lTTReqj9Xy/68m8FJKkpfd6Urr
jxfP3uJ2S7wv1guQn4JyfQ8eyVO5bUIml8so1YW686RDPOzAq21ZxHf0j6eC0q2G
bUvE+/0S7Db+Gnz58t8OsGoaCEeN1mnIEeK6+mR53LngQH5FZsvNUnMMmVIoHaHy
YHcF9nDiqcs6X0/s1NKUeJft+MJYDA/CSSHth9OJSIK2HlcW+epXbxzvXVIiT1RO
AS+jiFEEmLOnOWNSCSzYYmAs5HNL9YdLmqd4pu0d9HgvN5ZCBH98YXhBBL3NthV7
kGtLP4sBAoGBAP1e2YaPtzXgHuhGTUAZeQN8KDQhhn6iUfuSRQ5hbNsPSR9rvuxh
kJiQQgNgNUtacXa7/Pm9BeteszTocwTnQl3vIlyDJPogaytDwGdFqLf/RR/ULkse
6jCAB3Qt4orSRG5xH8QBpEhnBgS7T0Kid1xRmNxsbi7A58FBjasjOwEXAoGBAN1k
g592J9NDeuX0BMH6JT0fjq2FgB/lZrRDzuM7yAgDLcViQdW10DEXXxDBUfuXH4Qi
JFDenLLPYRVODSFbWIa9BodAs8XEEsG8zo8x/hTryEOf/0Zdoi2YtWuz/E5jllpK
YK/NU58tQWQCsQbMIPTRlBKhNXxTvKEQil28m5LPAoGBAIwhJ0FqvrNHTxC7wQHQ
lMM+qaWbXR0wfRMb5KF9dIz7OT/tgVyO4T/fmQLw9MjGLrayZclhp6Jzb721SdfO
Z0A4f9KWnZ7QyzTUddcoCZYp0ns2CJx3bqKATJ8OuZp5jGtgmWb4WXnJsORxC/cY
j9c5McfHGHE3M3YI4WdjRsDlAoGABlxr97nyXPyUXGUNefFQ/peYht3OF5yEvesw
15CRJ8HHn+M51wUZTT/JqHaVf3ARJL/CYVx0DiMtO+p5MBsqyPxHYr12LNl8XHqr
SKv8C+fWYjMHp6LrFPpNRCHwvuPXnxKCAqsYmvs25MO7CGH3FHGtGnftTHwvcEVE
ZHsV0TsCgYBmuhKnQnBYYrbs5Tr5xrU98ddaN+2acfLEzXkwhQxRAIvFOlUp2taP
6yAOiK8uxbQUgATYVeLHnCZAU1NevEw/IIjuRjnsSnnsyEB8Nw3K6kzwJIkodNaP
muvughaPDFil1tIouECfBuUkgDaIs5a8nQSpBbv8/SUhikIALQf6yA==
-----END RSA PRIVATE KEY-----"""


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