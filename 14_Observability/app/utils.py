import os
from dotenv import load_dotenv

def load_env():
    # Load .env if present
    load_dotenv()
    required = ["OPENAI_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing environment vars: {missing}")
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2", "false"),
        "LANGCHAIN_PROJECT": os.getenv("LANGCHAIN_PROJECT", "agentops_observability_demo"),
        "LANGCHAIN_API_KEY": os.getenv("LANGCHAIN_API_KEY", ""),
        "OPENAI_API_BASE": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        "HELICONE_API_KEY": os.getenv("HELICONE_API_KEY", ""),
        "HELICONE_USER_ID": os.getenv("HELICONE_USER_ID", "student_demo"),
        "HELICONE_PROJECT": os.getenv("HELICONE_PROJECT", "AgentOps_Demo"),
    }
