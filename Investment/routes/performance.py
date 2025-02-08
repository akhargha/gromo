# routes/performance.py
from flask import Blueprint, jsonify
from decimal import Decimal
from supabase_client import supabase
from services.stock_service import update_stock_prices

performance_bp = Blueprint("performance_bp", __name__)

@performance_bp.route("/investment_performance", methods=["GET"])
def investment_performance():
    """
    Shows real-time performance metrics for each investment_detail record.
    """
    details_resp = supabase.table("investment_details").select("*").execute()
    details = details_resp.data if details_resp.data else []

    performance_list = []
    for d in details:
        stock_symbol = d["stock_symbol"]
        stock_resp = supabase.table("stocks").select("*").eq("symbol", stock_symbol).single().execute()
        if stock_resp.data:
            stock_info = stock_resp.data
            current_price = Decimal(str(stock_info["current_price"]))
            previous_close = Decimal(str(stock_info["previous_close"]))
            units = Decimal(str(d["units"]))
            purchase_price = Decimal(str(d["purchase_price"]))

            current_value = (current_price * units).quantize(Decimal("0.01"))
            total_return = ((current_price - purchase_price) * units).quantize(Decimal("0.01"))
            todays_return = ((current_price - previous_close) * units).quantize(Decimal("0.01"))

            performance_list.append({
                "investment_detail_id": d["id"],
                "stock_symbol": stock_symbol,
                "units": str(units),
                "purchase_price": str(purchase_price),
                "current_price": str(current_price),
                "previous_close": str(previous_close),
                "current_value": str(current_value),
                "total_return": str(total_return),
                "todays_return": str(todays_return),
            })

    return jsonify(performance_list), 200

@performance_bp.route("/update_stock_prices", methods=["GET"])
def update_stocks():
    """
    An optional endpoint to manually trigger the Yahoo Finance update
    for all stocks in our 'stocks' table.
    """
    msg = update_stock_prices()
    return jsonify({"message": msg}), 200
