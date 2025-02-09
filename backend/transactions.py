from flask import Flask, request, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client
import os
from datetime import datetime
from flask_cors import CORS

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

def update_credit_card_for_transaction(amount, cashback):
    """Helper function to update credit card details after a transaction"""
    try:
        # Get current credit card details
        credit_card = supabase.table("credit_card").select("*").single().execute()
        
        if not credit_card.data:
            raise APIError("Credit card not found", 404)
        
        card_data = credit_card.data
        
        # Calculate new values
        new_balance = float(card_data['curr_balance']) + float(amount)
        new_available_credit = float(card_data['credit_limit']) - new_balance
        new_rewards_cash = float(card_data['rewards_cash']) + float(cashback)
        
        # Validate transaction
        if new_available_credit < 0:
            raise APIError("Insufficient credit available", 400)
        
        # Update credit card
        update_data = {
            'curr_balance': new_balance,
            'available_credit': new_available_credit,
            'rewards_cash': new_rewards_cash
        }
        
        result = supabase.table("credit_card").update(update_data).neq("id", None).execute()
        
        if not result.data:
            raise APIError("Failed to update credit card", 500)
            
        return result.data[0]
        
    except Exception as e:
        raise APIError(str(e), 500)

@app.route("/transactions", methods=["POST"])
def create_transaction():
    try:
        data = request.json
        required_fields = ["amount"]
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                raise APIError(f"Missing required field: {field}", 400)
        
        amount = float(data["amount"])
        
        # Get current credit card details first
        credit_card_response = supabase.table("credit_card").select("*").single().execute()
        if not credit_card_response.data:
            raise APIError("No credit card found in the system", 404)
        
        card_data = credit_card_response.data
        
        # Validate if transaction is possible
        new_balance = float(card_data['curr_balance']) + amount
        if new_balance > float(card_data['credit_limit']):
            raise APIError("Transaction would exceed credit limit", 400)
        
        # Create transaction
        transaction = {
            "amount": amount,
            "transaction_date": datetime.now().isoformat(),
            "invested": False
        }
        
        # Insert transaction first
        transaction_result = supabase.table("transactions").insert(transaction).execute()
        
        if not transaction_result.data:
            raise APIError("Failed to create transaction", 500)
        
        # Update credit card
        new_available_credit = float(card_data['credit_limit']) - new_balance
        update_data = {
            'curr_balance': new_balance,
            'available_credit': new_available_credit,
            # cashback is auto-calculated in the transactions table,
            # so we need to add it to existing rewards_cash
            'rewards_cash': float(card_data['rewards_cash']) + (amount * 0.03)
        }
        
        card_result = supabase.table("credit_card").update(update_data).eq("id", card_data['id']).execute()
        
        if not card_result.data:
            # If credit card update fails, we should delete the transaction
            supabase.table("transactions").delete().eq("id", transaction_result.data[0]['id']).execute()
            raise APIError("Failed to update credit card", 500)
        
        response_data = {
            "transaction": transaction_result.data[0],
            "credit_card": card_result.data[0]
        }
        
        return jsonify(response_data), 201
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(str(e), 500)
    
    
@app.route("/transactions", methods=["GET"])
def get_transactions():
    try:
        # Get query parameters
        limit = request.args.get("limit", 10, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        # Query transactions
        result = supabase.table("transactions")\
                         .select("*")\
                         .order("transaction_date", desc=True)\
                         .range(offset, offset + limit - 1)\
                         .execute()            
        return jsonify(result.data), 200
        
    except Exception as e:
        raise APIError(str(e), 500)

@app.route("/transactions/invest/<uuid:transaction_id>", methods=["POST"])
def invest_cashback(transaction_id):
    try:
        # Get transaction
        transaction = supabase.table("transactions")\
            .select("*")\
            .eq("id", str(transaction_id))\
            .execute()
            
        if not transaction.data:
            raise APIError("Transaction not found", 404)
            
        if transaction.data[0]["invested"]:
            raise APIError("Cashback already invested", 400)
        
        # Update transaction
        result = supabase.table("transactions")\
            .update({"invested": True})\
            .eq("id", str(transaction_id))\
            .execute()
            
        return jsonify(result.data[0]), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(str(e), 500)

if __name__ == "__main__":
    app.run(debug=True, port=5003)
