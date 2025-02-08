# routes/portfolios.py
from flask import Blueprint, jsonify
from supabase_client import supabase

portfolios_bp = Blueprint("portfolios_bp", __name__)

@portfolios_bp.route("/portfolios", methods=["GET"])
def get_portfolios():
    """
    Returns available investment portfolios with metadata 
    and underlying stock allocations.
    """
    portfolio_resp = supabase.table("portfolios").select("*").execute()
    portfolios = portfolio_resp.data if portfolio_resp.data else []

    result = []
    for p in portfolios:
        portfolio_id = p["id"]
        # fetch associated stocks from 'portfolio_stocks'
        mapping_resp = supabase.table("portfolio_stocks").select("*").eq("portfolio_id", portfolio_id).execute()
        mapping_data = mapping_resp.data if mapping_resp.data else []

        stocks_list = []
        for entry in mapping_data:
            stock_symbol = entry["stock_symbol"]
            # fetch from 'stocks' table
            stock_resp = supabase.table("stocks").select("*").eq("symbol", stock_symbol).single().execute()
            stock_data = stock_resp.data
            if stock_data:
                stocks_list.append({
                    "symbol": stock_data["symbol"],
                    "name": stock_data["name"],
                    "weight": str(entry["weight"])
                })

        result.append({
            "id": p["id"],
            "name": p["name"],
            "description": p.get("description"),
            "historical_return": str(p.get("historical_return", 0)),
            "risk_level": p.get("risk_level", "Medium"),
            "stocks": stocks_list
        })

    return jsonify(result), 200
