import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from datetime import datetime
import yfinance as yf
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("REACT_APP_SUPABASE_URL"),
    os.getenv("REACT_APP_SUPABASE_ANON_KEY")
)

class APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__()
        self.message = message
        self.status_code = status_code

@app.errorhandler(APIError)
def handle_exception(err):
    response = {"error": err.message}
    return jsonify(response), err.status_code

import yfinance as yf

def get_current_stock_price(symbol="^GSPC"):
    """Get the current S&P 500 price using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        
        # **Preferred Method: Use `.fast_info['last_price']` for real-time prices**
        current_price = ticker.fast_info.get("last_price")
        
        # **Fallback: Use `history()` for the latest close price if `fast_info` fails**
        if current_price is None:
            history = ticker.history(period="1d")
            if not history.empty:
                current_price = history["Close"].iloc[-1]
        
        if current_price is None:
            raise APIError("Unable to fetch current stock price", 500)
        
        return float(current_price)
    
    except Exception as e:
        raise APIError(f"Error fetching stock price: {str(e)}", 500)


def invest_rewards_cash():
    """Process investment of all available rewards cash"""
    try:
        # Get current credit card details
        credit_card = supabase.table("credit_card").select("*").eq("credit_limit", 10000).execute()
        
        if not credit_card.data:
            raise APIError("Credit card not found", 404)
        
        rewards_cash = float(credit_card.data[0]['rewards_cash'])
        if rewards_cash <= 0:
            raise APIError("No rewards cash available to invest", 400)
        
        # Get current S&P 500 price
        current_price = get_current_stock_price()
        
        # Calculate units that can be purchased
        units = rewards_cash / current_price
        
        # Create investment record
        investment_data = {
            "amount_invested": rewards_cash,
            "index_purchased": "S&P 500",
            "units_purchased": round(units, 4),
            "price_per_unit": current_price,
            "date": datetime.now().isoformat()
        }
        
        # Insert investment record
        investment_result = supabase.table("investments").insert(investment_data).execute()
        
        if not investment_result.data:
            raise APIError("Failed to create investment record", 500)
        
        # Update credit card rewards to 0
        card_update = supabase.table("credit_card")\
            .update({"rewards_cash": 0})\
            .eq("credit_limit", 10000)\
            .execute()
            
        if not card_update.data:
            # Rollback investment if card update fails
            supabase.table("investments")\
                .delete()\
                .eq("id", investment_result.data[0]['id'])\
                .execute()
            raise APIError("Failed to update credit card rewards", 500)
        
        # Mark all transactions as invested
        transaction_update = supabase.table("transactions")\
            .update({"invested": True})\
            .eq("invested", False)\
            .execute()
            
        return investment_result.data[0]
        
    except Exception as e:
        raise APIError(str(e), 500)

@app.route("/investments", methods=["GET"])
def get_investments():
    """Get all investments with optional pagination"""
    try:
        limit = request.args.get("limit", 10, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        result = supabase.table("investments")\
            .select("*")\
            .order("date", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
            
        return jsonify(result.data), 200
        
    except Exception as e:
        raise APIError(str(e), 500)

@app.route("/investments/total", methods=["GET"])
def get_investment_summary():
    """Get total investment summary"""
    try:
        result = supabase.table("investments")\
            .select("*")\
            .execute()
            
        if not result.data:
            return jsonify({
                "total_amount_invested": 0,
                "total_units_purchased": 0,
                "current_value": 0,
                "total_return": 0
            }), 200
            
        total_amount = sum(float(inv['amount_invested']) for inv in result.data)
        total_units = sum(float(inv['units_purchased']) for inv in result.data)
        
        # Get current value
        current_price = get_current_stock_price()
        current_value = total_units * current_price
        total_return = current_value - total_amount
        
        summary = {
            "total_amount_invested": total_amount,
            "total_units_purchased": total_units,
            "current_value": current_value,
            "total_return": total_return
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        raise APIError(str(e), 500)

@app.route("/investments/invest-rewards", methods=["GET"])
def create_investment():
    """Create new investment from available rewards cash"""
    try:
        result = invest_rewards_cash()
        return jsonify(result), 201
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(str(e), 500)

if __name__ == "__main__":
    app.run(debug=True, port=5002)