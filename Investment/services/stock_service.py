import yfinance as yf
from decimal import Decimal
from supabase_client import supabase
from typing import Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def update_stock_prices() -> Dict[str, Any]:
    """
    Asynchronously fetch updated prices from Yahoo Finance for each stock.
    """
    stocks_resp = supabase.table("stocks").select("symbol").execute()
    all_stocks = stocks_resp.data if stocks_resp.data else []

    if not all_stocks:
        return {"status": "error", "message": "No stocks found to update."}

    async def update_single_stock(stock: Dict[str, str]) -> Dict[str, Any]:
        symbol = stock["symbol"]
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return {"symbol": symbol, "status": "error", "message": "No data available"}

            last_two = hist.tail(2)
            current_close = Decimal(str(last_two.iloc[-1]["Close"]))
            prev_close = Decimal(str(last_two.iloc[-2]["Close"])) if len(last_two) > 1 else current_close

            # Update in Supabase
            supabase.table("stocks").update({
                "current_price": str(current_close),
                "previous_close": str(prev_close),
                "updated_at": "NOW()"
            }).eq("symbol", symbol).execute()

            return {
                "symbol": symbol,
                "status": "success",
                "current_price": str(current_close),
                "prev_close": str(prev_close)
            }
        except Exception as e:
            return {"symbol": symbol, "status": "error", "message": str(e)}

    # Use ThreadPoolExecutor for concurrent API calls
    with ThreadPoolExecutor(max_workers=10) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, update_single_stock, stock)
            for stock in all_stocks
        ]
        results = await asyncio.gather(*tasks)

    return {
        "status": "success",
        "updates": results
    }