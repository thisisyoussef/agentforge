"""Tests for the /agent/chat endpoint.

TDD Red phase: these tests define the contract for the agent chat API.
Both must fail before implementation begins.
"""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _require_anthropic_key():
    """Skip agent chat tests if ANTHROPIC_API_KEY is not set."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set")


def test_chat_market_question():
    """POST /agent/chat with market question returns 200 with price and tool_calls."""
    response = client.post(
        "/agent/chat",
        json={"message": "What is the current price of AAPL?", "session_id": "test-1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert "session_id" in body
    assert body["session_id"] == "test-1"
    assert "tool_calls" in body
    assert len(body["tool_calls"]) > 0
    # The response text should mention a price (numeric)
    assert any(char.isdigit() for char in body["response"])


def test_chat_empty_message():
    """POST /agent/chat with empty message returns 200, not 500."""
    response = client.post(
        "/agent/chat",
        json={"message": "", "session_id": "test-2"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert "session_id" in body
