import os
from dotenv import load_dotenv

def load_env():
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment.")
    return key
