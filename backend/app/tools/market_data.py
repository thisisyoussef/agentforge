"""Market data fetch tool using Yahoo Finance.

Provides structured financial data for stock tickers.
Designed to be used as a LangGraph tool node.
"""

from __future__ import annotations

import yfinance as yf
from pydantic import BaseModel


class MarketDataOutput(BaseModel):
    """Structured output for a single ticker's market data."""

    symbol: str
    name: str | None = None
    price: float | None = None
    pe_ratio: float | None = None
    dividend_yield: float | None = None
    market_cap: int | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    error: str | None = None


def market_data_fetch(symbols: str | list[str]) -> dict[str, MarketDataOutput]:
    """Fetch market data for one or more ticker symbols.

    Args:
        symbols: A single ticker string or list of ticker strings.

    Returns:
        Dict mapping each symbol to its MarketDataOutput.
        Invalid symbols get an error field instead of raising.
    """
    if isinstance(symbols, str):
        symbols = [symbols]

    results: dict[str, MarketDataOutput] = {}
    for symbol in symbols:
        symbol = symbol.strip().upper()
        results[symbol] = _fetch_single(symbol)
    return results


def _fetch_single(symbol: str) -> MarketDataOutput:
    """Fetch data for a single ticker, returning error info on failure."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # yfinance returns minimal info for invalid tickers
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        name = info.get("shortName")

        if price is None and name is None:
            return MarketDataOutput(
                symbol=symbol,
                error=f"Could not find data for {symbol}. The symbol may be invalid.",
            )

        return MarketDataOutput(
            symbol=symbol,
            name=name,
            price=price,
            pe_ratio=info.get("trailingPE"),
            dividend_yield=info.get("dividendYield"),
            market_cap=info.get("marketCap"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
        )
    except Exception as exc:
        return MarketDataOutput(
            symbol=symbol,
            error=f"Could not find data for {symbol}: {exc}",
        )
