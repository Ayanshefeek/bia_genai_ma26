import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


def main():
    load_dotenv()

    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.7
        )
    msg = [HumanMessage(content="In exactly 3 bullet points, define observability for AI Agents")]
    resp = llm.invoke(msg)

    print(resp.content)

if __name__ == "__main__":
    main()