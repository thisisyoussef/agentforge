from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

app = FastAPI(title="AgentForge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Existing endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "agentforge-backend",
        "message": "AgentForge backend with market data agent.",
    }


# ---------------------------------------------------------------------------
# Agent chat endpoint
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    session_id: str = ""


class ToolCallInfo(BaseModel):
    name: str
    args: dict
    result: str | None = None


class ChatResponse(BaseModel):
    response: str
    tool_calls: list[ToolCallInfo]
    session_id: str


@app.post("/agent/chat", response_model=ChatResponse)
def agent_chat(req: ChatRequest) -> ChatResponse:
    """Single-turn agent chat: send a message, get a response with tool calls."""
    from app.agent.graph import agent_graph

    if not req.message.strip():
        return ChatResponse(
            response="Please provide a message to get started.",
            tool_calls=[],
            session_id=req.session_id,
        )

    try:
        result = agent_graph.invoke(
            {"messages": [HumanMessage(content=req.message)]}
        )

        messages = result["messages"]

        # Extract tool call info from the conversation
        tool_calls: list[ToolCallInfo] = []
        for msg in messages:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls.append(
                        ToolCallInfo(name=tc["name"], args=tc["args"])
                    )

        # Attach tool results to their corresponding calls
        from langchain_core.messages import ToolMessage

        tool_results = [m for m in messages if isinstance(m, ToolMessage)]
        for i, tr in enumerate(tool_results):
            if i < len(tool_calls):
                tool_calls[i].result = tr.content

        # Final response is the last AI message without tool calls
        final_response = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                final_response = msg.content
                break

        return ChatResponse(
            response=final_response or "I processed your request but have no text response.",
            tool_calls=tool_calls,
            session_id=req.session_id,
        )
    except Exception as exc:
        return ChatResponse(
            response=f"An error occurred: {exc}",
            tool_calls=[],
            session_id=req.session_id,
        )
