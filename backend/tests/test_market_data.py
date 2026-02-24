"""Tests for the market_data_fetch tool.

TDD Red phase: these tests define the contract for market_data_fetch.
All 3 must fail before implementation begins.
"""

from app.tools.market_data import market_data_fetch, MarketDataOutput


def test_fetch_valid_symbol():
    """market_data_fetch("AAPL") returns a dict with price > 0."""
    result = market_data_fetch("AAPL")

    assert isinstance(result, dict)
    assert "AAPL" in result
    data = result["AAPL"]
    assert isinstance(data, MarketDataOutput)
    assert data.price is not None
    assert data.price > 0
    assert data.name is not None
    assert data.error is None


def test_fetch_invalid_symbol():
    """market_data_fetch("XYZNOTREAL") returns error info, no exception."""
    result = market_data_fetch("XYZNOTREAL")

    assert isinstance(result, dict)
    assert "XYZNOTREAL" in result
    data = result["XYZNOTREAL"]
    assert isinstance(data, MarketDataOutput)
    assert data.error is not None
    assert "XYZNOTREAL" in data.error


def test_fetch_multiple_symbols():
    """market_data_fetch(["MSFT", "GOOGL"]) returns data for both."""
    result = market_data_fetch(["MSFT", "GOOGL"])

    assert isinstance(result, dict)
    assert "MSFT" in result
    assert "GOOGL" in result
    assert result["MSFT"].price is not None
    assert result["MSFT"].price > 0
    assert result["GOOGL"].price is not None
    assert result["GOOGL"].price > 0
