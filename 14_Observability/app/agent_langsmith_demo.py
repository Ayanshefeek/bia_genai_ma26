import os
from dotenv import load_dotenv
from typing import Annotated
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.graph import END, START
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage



load_dotenv()

class State(TypedDict):
    """State for the agent."""
    messages: Annotated[list[BaseMessage], add_messages]

model = ChatOpenAI(temperature =0)


def make_graph():
    @tool
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    tool_node = ToolNode([add])
    model_with_tool = model.bind_tools([add])
    def call_model(state):
        messages = state["messages"]
        response = model_with_tool.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: State):
        if state["messages"][-1].tool_calls:
            return "tools"
        else:
            return END
        
    graph = StateGraph(State)

    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    agent = graph.compile()
    return agent

agent = make_graph()
agent.invoke({"messages":["What is 2+3"]})
