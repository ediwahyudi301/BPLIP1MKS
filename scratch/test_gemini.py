import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    resp = requests.get(
        f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    )
    print("Status code:", resp.status_code)
    print("Response json:", resp.json())
