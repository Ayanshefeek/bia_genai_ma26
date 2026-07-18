"""Helicone analytics demo.
Routes OpenAI requests through the Helicone proxy for cost/latency tracking.

Run:
  python app/helicone_demo.py
Then open Helicone dashboard to view analytics.
"""
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI
def main():
    load_dotenv()
    # Route via Helicone proxy if provided
    # openai.api_key = env["OPENAI_API_KEY"]
    # print(openai.__version__)
    # openai.base_url = env["OPENAI_API_BASE"]
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://oai.helicone.ai/v1",
    )
    headers = {
        "Helicone-Auth": f"Bearer {os.getenv('HELICONE_API_KEY')}",
        "Helicone-Target-Provider": "openai",
        "Helicone-User-Id": os.getenv("HELICONE_USER_ID"),
        "Helicone-Property-Project": os.getenv("HELICONE_PROJECT"),
    }
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Summarize observability in one sentence."}],
            extra_headers=headers
        )
        print(completion.choices[0].message.content)
    except Exception as e:
        print(type(e))
        print(e)
        if hasattr(e, "response"):
            print(e.response.text)

if __name__ == "__main__":
    main()
