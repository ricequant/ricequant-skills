import os
import pandas as pd
import rqdatac
from fastmcp import FastMCP
from datetime import datetime, date
from typing import Optional, List, Union, Any

# Initialize FastMCP server
mcp = FastMCP("Ricequant SDK Server")

# Global flag for rqdatac initialization
_RQDATA_INITIALIZED = False

def ensure_rqdata():
    """Ensure rqdatac is initialized."""
    global _RQDATA_INITIALIZED
    if not _RQDATA_INITIALIZED:
        # rqdatac.init() uses environment variables or local config
        rqdatac.init()
        _RQDATA_INITIALIZED = True

@mcp.tool()
def all_instruments(
    type: Optional[str] = None,
    date: Optional[str] = None,
    market: str = "cn"
) -> str:
    """
    Get basic information of all instruments in a specific market.
    
    Args:
        type: Instrument type (e.g., 'CS' for Common Stock, 'Future', 'Option', 'ETF', 'INDX', 'Convertible').
        date: Target date to filter active instruments (YYYYMMDD or YYYY-MM-DD).
        market: Market code, 'cn' for Mainland China, 'hk' for Hong Kong.
    """
    ensure_rqdata()
    df = rqdatac.all_instruments(type=type, date=date, market=market)
    if df is None or df.empty:
        return "No instruments found."
    return df.to_csv(index=False)

@mcp.tool()
def get_price(
    order_book_ids: Union[str, List[str]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    frequency: str = "1d",
    fields: Optional[Union[str, List[str]]] = None,
    adjust_type: str = "pre",
    skip_suspended: bool = False,
    market: str = "cn"
) -> str:
    """
    Get historical price data (OHLCV) for specified instruments.
    
    Args:
        order_book_ids: One or more instrument identifiers (e.g., '000001.XSHE').
        start_date: Start date (YYYYMMDD or YYYY-MM-DD).
        end_date: End date (YYYYMMDD or YYYY-MM-DD).
        frequency: Data frequency ('1d', '1m', '5m', '1w', 'tick').
        fields: Specific fields to retrieve (e.g., 'open', 'close', 'low', 'high', 'volume').
        adjust_type: Price adjustment type ('pre', 'post', 'none').
        skip_suspended: Whether to skip suspended days.
        market: Market code ('cn' or 'hk').
    """
    ensure_rqdata()
    # Handle single string or list of strings
    df = rqdatac.get_price(
        order_book_ids=order_book_ids,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        fields=fields,
        adjust_type=adjust_type,
        skip_suspended=skip_suspended,
        market=market,
        expect_df=True
    )
    
    if df is None or df.empty:
        return "No price data found."
    
    return df.to_csv()

@mcp.tool()
def get_quota() -> str:
    """Get the current RQData traffic quota and license information."""
    ensure_rqdata()
    quota = rqdatac.user.get_quota()
    return str(quota)

@mcp.tool()
def info() -> str:
    """Get the current RQData version and server information."""
    ensure_rqdata()
    # rqdatac.info() prints to stdout, we might need to capture it or just return version
    return f"rqdatac version: {rqdatac.__version__}"

if __name__ == "__main__":
    mcp.run()
