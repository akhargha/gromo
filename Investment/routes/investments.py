# investments.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Optional, Any
from supabase_client import supabase

investments_bp = Blueprint("investments_bp", __name__)

def get_single_card() -> Optional[Dict[str, Any]]:
    """Retrieve the single credit card record."""
    response = supabase.table("credit_cards").select("*").limit(1).execute()
    return response.data[0] if response.data else None

def update_credit_card(card_id: int, fields: Dict[str, Any]) -> None:
    """Update credit card fields."""
    supabase.table("credit_cards").update(fields).eq("id", card_id).execute()

def get_stock_by_id(stock_id: int) -> Optional[Dict[str, Any]]:
    """Get stock details by ID."""
    response = supabase.table("stocks").select("*").eq("id", stock_id).single().execute()
    return response.data if response.data else None

@investments_bp.route("/invest", methods=["POST"])
def invest():
    """Process a manual investment request."""
    try:
        data = request.get_json() or {}
        amount_str = data.get("amount")
        portfolio_name = data.get("portfolio")

        if not amount_str or not portfolio_name:
            return jsonify({"message": "Amount and portfolio are required"}), 400

        # Get credit card
        card = get_single_card()
        if not card:
            return jsonify({"message": "No credit card record found"}), 404

        amount = Decimal(str(amount_str))
        current_cash = Decimal(str(card["rewards_cash"]))
        if amount > current_cash:
            return jsonify({"message": "Not enough cashback available"}), 400

        # Get portfolio - using exact name match
        portfolio_resp = supabase.table("portfolios").select("*").eq("name", portfolio_name).execute()
        if not portfolio_resp.data or len(portfolio_resp.data) == 0:
            return jsonify({"message": "Portfolio not found", "available_portfolios": ["Tech Growth", "Balanced Mix", "Conservative"]}), 404
        portfolio = portfolio_resp.data[0]

        # Create investment record
        inv_payload = {
            "credit_card_id": card["id"],
            "investment_date": str(datetime.utcnow()),
            "investment_amount": str(amount),
            "portfolio": portfolio["name"]
        }
        inv_resp = supabase.table("investments").insert(inv_payload).execute()
        if not inv_resp.data:
            return jsonify({"message": "Failed to create investment"}), 500
        investment_id = inv_resp.data[0]["id"]

        # Get portfolio stocks with stock details
        allocations = []
        port_stocks_resp = supabase.table("portfolio_stocks").select("*").eq("portfolio_id", portfolio["id"]).execute()
        portfolio_stocks = port_stocks_resp.data if port_stocks_resp.data else []

        for ps in portfolio_stocks:
            stock = get_stock_by_id(ps["stock_id"])
            if stock:
                weight = Decimal(str(ps["weight"]))
                alloc_amount = (amount * weight / Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
                current_price = Decimal(str(stock["current_price"]))
                
                units = (alloc_amount / current_price).quantize(Decimal("0.0001"), rounding=ROUND_DOWN) if current_price > 0 else Decimal(0)
                
                # Record the investment detail
                supabase.table("investment_details").insert({
                    "investment_id": investment_id,
                    "stock_id": stock["id"],  # Using stock_id instead of symbol
                    "units": str(units),
                    "purchase_price": str(current_price)
                }).execute()
                
                allocations.append({
                    "stock_symbol": stock["symbol"],
                    "units": str(units),
                    "amount_allocated": str(alloc_amount)
                })

        # Update credit card balance
        new_cash = current_cash - amount
        update_credit_card(card["id"], {
            "rewards_cash": str(new_cash),
            "updated_at": str(datetime.utcnow())
        })

        return jsonify({
            "message": "Investment completed",
            "portfolio": portfolio["name"],
            "amount_invested": str(amount),
            "allocations": allocations
        }), 200

    except Exception as e:
        return jsonify({"message": f"Error processing investment: {str(e)}"}), 500

@investments_bp.route("/auto_invest", methods=["POST"])
def auto_invest():
    """Auto-invest available rewards cash."""
    try:
        card = get_single_card()
        if not card:
            return jsonify({"message": "No credit card record found"}), 404

        total_cashback = Decimal(str(card["rewards_cash"]))
        if total_cashback <= 0:
            return jsonify({"message": "No cashback available for auto-investment"}), 400

        # Get best performing portfolio
        portfolios_resp = supabase.table("portfolios").select("*").order("historical_return", desc=True).limit(1).execute()
        if not portfolios_resp.data:
            return jsonify({"message": "No portfolio available"}), 400
        portfolio = portfolios_resp.data[0]

        # Create investment record
        inv_resp = supabase.table("investments").insert({
            "credit_card_id": card["id"],
            "investment_date": str(datetime.utcnow()),
            "investment_amount": str(total_cashback),
            "portfolio": portfolio["name"]
        }).execute()
        if not inv_resp.data:
            return jsonify({"message": "Failed to create investment"}), 500
        investment_id = inv_resp.data[0]["id"]

        # Process allocations
        allocations = []
        port_stocks_resp = supabase.table("portfolio_stocks").select("*").eq("portfolio_id", portfolio["id"]).execute()
        portfolio_stocks = port_stocks_resp.data if port_stocks_resp.data else []

        for ps in portfolio_stocks:
            stock = get_stock_by_id(ps["stock_id"])
            if stock:
                weight = Decimal(str(ps["weight"]))
                alloc_amount = (total_cashback * weight / Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
                current_price = Decimal(str(stock["current_price"]))
                
                units = (alloc_amount / current_price).quantize(Decimal("0.0001"), rounding=ROUND_DOWN) if current_price > 0 else Decimal(0)
                
                supabase.table("investment_details").insert({
                    "investment_id": investment_id,
                    "stock_id": stock["id"],
                    "units": str(units),
                    "purchase_price": str(current_price)
                }).execute()
                
                allocations.append({
                    "stock_symbol": stock["symbol"],
                    "units": str(units),
                    "amount_allocated": str(alloc_amount)
                })

        # Update credit card balance
        update_credit_card(card["id"], {
            "rewards_cash": "0.00",
            "updated_at": str(datetime.utcnow())
        })

        return jsonify({
            "message": "Auto-investment completed",
            "portfolio": portfolio["name"],
            "amount_invested": str(total_cashback),
            "allocations": allocations
        }), 200

    except Exception as e:
        return jsonify({"message": f"Error processing auto-investment: {str(e)}"}), 500

@investments_bp.route("/investment_summary", methods=["GET"])
def investment_summary():
    """Get investment summary with current values."""
    try:
        investments_resp = supabase.table("investments").select("*").execute()
        result = []

        for inv in investments_resp.data or []:
            details_resp = supabase.table("investment_details").select("*").eq("investment_id", inv["id"]).execute()
            allocations = []
            total_current_value = Decimal("0")

            for detail in details_resp.data or []:
                stock = get_stock_by_id(detail["stock_id"])
                if stock:
                    units = Decimal(str(detail["units"]))
                    purchase_price = Decimal(str(detail["purchase_price"]))
                    current_price = Decimal(str(stock["current_price"]))
                    
                    position_value = units * current_price
                    total_current_value += position_value
                    
                    allocations.append({
                        "stock_symbol": stock["symbol"],
                        "units": str(units),
                        "purchase_price": str(purchase_price),
                        "current_price": str(current_price),
                        "current_value": str(position_value)
                    })

            result.append({
                "investment_id": inv["id"],
                "investment_date": inv["investment_date"],
                "portfolio": inv["portfolio"],
                "investment_amount": inv["investment_amount"],
                "current_value": str(total_current_value),
                "allocations": allocations
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"message": f"Error fetching investment summary: {str(e)}"}), 500