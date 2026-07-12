import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def main():
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url="https://api.helicone.ai/v1",
    )

    headers = {
        "Helicone-Auth": f"Bearer {os.environ.get('HELICONE_API_KEY')}",
        "Helicone-Target-Provider": "openai",
        "Helicone-User-Id": os.environ.get("HELICONE_USER_ID"),
        "Helicone-Property-Project": os.environ.get("HELICONE_PROJECT"),
    }
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Summarize observability in one sentence."}],
            extra_headers=headers
        )
        print(completion.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()