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
def get_trading_dates(
    start_date: str,
    end_date: str,
    market: str = "cn"
) -> str:
    """
    Get a list of trading dates within a specified range.
    
    Args:
        start_date: Start date (YYYYMMDD or YYYY-MM-DD).
        end_date: End date (YYYYMMDD or YYYY-MM-DD).
        market: Market code ('cn' or 'hk').
    """
    ensure_rqdata()
    dates = rqdatac.get_trading_dates(start_date=start_date, end_date=end_date, market=market)
    if not dates:
        return "No trading dates found."
    return "\n".join([d.strftime("%Y-%m-%d") for d in dates])

@mcp.tool()
def index_components(
    order_book_id: str,
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market: str = "cn"
) -> str:
    """
    Get constituents of a specific index.
    
    Args:
        order_book_id: Index identifier (e.g., '000300.XSHG').
        date: Target date.
        start_date: Start date for range query.
        end_date: End date for range query.
        market: Market code ('cn' or 'hk').
    """
    ensure_rqdata()
    res = rqdatac.index_components(
        order_book_id=order_book_id,
        date=date,
        start_date=start_date,
        end_date=end_date,
        market=market
    )
    if res is None:
        return "No index components found."
    
    if isinstance(res, list):
        return "\n".join(res)
    elif isinstance(res, dict):
        # Handle date range result (dict mapping dates to lists)
        output = []
        for d, ids in sorted(res.items()):
            output.append(f"{d}: {', '.join(ids)}")
        return "\n".join(output)
    return str(res)

@mcp.tool()
def get_factor(
    order_book_ids: Union[str, List[str]],
    factor: Union[str, List[str]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market: str = "cn"
) -> str:
    """
    Get factor values for specified instruments and dates.
    
    Args:
        order_book_ids: One or more instrument identifiers.
        factor: Factor name(s).
        start_date: Start date (YYYYMMDD or YYYY-MM-DD).
        end_date: End date (YYYYMMDD or YYYY-MM-DD).
        market: Market code ('cn' or 'hk').
    """
    ensure_rqdata()
    df = rqdatac.get_factor(
        order_book_ids=order_book_ids,
        factor=factor,
        start_date=start_date,
        end_date=end_date,
        market=market,
        expect_df=True
    )
    if df is None or df.empty:
        return "No factor data found."
    return df.to_csv()

@mcp.tool()
def get_pit_financials_ex(
    order_book_ids: Union[str, List[str]],
    fields: List[str],
    start_quarter: str,
    end_quarter: str,
    date: Optional[str] = None,
    statements: str = "latest",
    market: str = "cn"
) -> str:
    """
    Get Point-In-Time financial data (modern replacement for get_fundamentals).
    
    Args:
        order_book_ids: One or more instrument identifiers.
        fields: Financial fields to retrieve (e.g., 'revenue', 'net_profit').
        start_quarter: Start quarter (e.g., '2023q1').
        end_quarter: End quarter (e.g., '2023q4').
        date: Observation date (optional).
        statements: 'latest' or 'all'.
        market: Market code ('cn' or 'hk').
    """
    ensure_rqdata()
    df = rqdatac.get_pit_financials_ex(
        order_book_ids=order_book_ids,
        fields=fields,
        start_quarter=start_quarter,
        end_quarter=end_quarter,
        date=date,
        statements=statements,
        market=market
    )
    if df is None or df.empty:
        return "No financial data found."
    return df.to_csv()

@mcp.tool()
def info() -> str:
    """Get the current RQData version and server information."""
    ensure_rqdata()
    return f"rqdatac version: {rqdatac.__version__}"

if __name__ == "__main__":
    mcp.run()
