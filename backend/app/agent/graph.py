"""LangGraph agent with market data tool.

Implements the reasoning → tool → respond loop using StateGraph.
"""

from __future__ import annotations

import json
import os
from typing import Annotated

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from app.tools.market_data import market_data_fetch as _raw_fetch


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ---------------------------------------------------------------------------
# Tool definition (LangChain-compatible wrapper)
# ---------------------------------------------------------------------------

@tool
def market_data_fetch(symbols: str) -> str:
    """Fetch real-time market data for stock ticker symbols.

    Args:
        symbols: Comma-separated ticker symbols (e.g. "AAPL" or "MSFT,GOOGL").

    Returns:
        JSON string with market data for each symbol.
    """
    symbol_list = [s.strip() for s in symbols.split(",")]
    if len(symbol_list) == 1:
        result = _raw_fetch(symbol_list[0])
    else:
        result = _raw_fetch(symbol_list)
    return json.dumps({k: v.model_dump() for k, v in result.items()}, indent=2)


TOOLS = [market_data_fetch]


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------

def _get_llm() -> ChatAnthropic:
    """Create the LLM with tools bound."""
    model_name = os.environ.get("MODEL_NAME", "claude-sonnet-4-20250514")
    return ChatAnthropic(
        model=model_name,
        temperature=0,
        max_tokens=4096,
    ).bind_tools(TOOLS)


def reasoning_node(state: AgentState) -> dict:
    """Invoke the LLM; it may request tool calls."""
    llm = _get_llm()
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


tool_node = ToolNode(TOOLS)


def should_continue(state: AgentState) -> str:
    """Route to tools if the last message has tool_calls, else end."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


# ---------------------------------------------------------------------------
# Build compiled graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    """Build and compile the agent graph."""
    graph = StateGraph(AgentState)
    graph.add_node("agent", reasoning_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


# Module-level compiled graph (lazy-initialized on first import in prod).
agent_graph = build_graph()
