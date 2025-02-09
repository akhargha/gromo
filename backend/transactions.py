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
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Error handler
class APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__()
        self.message = message
        self.status_code = status_code

@app.errorhandler(APIError)
def handle_exception(err):
    response = {"error": err.message}
    return jsonify(response), err.status_code

# Routes
@app.route("/transactions", methods=["POST"])
def create_transaction():
    try:
        data = request.json
        required_fields = ["amount"]
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                raise APIError(f"Missing required field: {field}", 400)
        
        # Create transaction
        transaction = {
            "amount": data["amount"],
            "transaction_date": datetime.now().isoformat(),
            "invested": False
        }
        
        result = supabase.table("transactions").insert(transaction).execute()
        
        return jsonify(result.data[0]), 201
        
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
            .limit(limit)\
            .offset(offset)\
            .execute()
            
        return jsonify(result.data), 200
        
    except Exception as e:
        raise APIError(str(e), 500)

@app.route("/transactions/<uuid:transaction_id>", methods=["GET"])
def get_transaction(transaction_id):
    try:
        result = supabase.table("transactions")\
            .select("*")\
            .eq("id", str(transaction_id))\
            .execute()
            
        if not result.data:
            raise APIError("Transaction not found", 404)
            
        return jsonify(result.data[0]), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(str(e), 500)

@app.route("/transactions/<uuid:transaction_id>", methods=["PATCH"])
def update_transaction(transaction_id):
    try:
        data = request.json
        
        # Check if transaction exists
        exists = supabase.table("transactions")\
            .select("id")\
            .eq("id", str(transaction_id))\
            .execute()
            
        if not exists.data:
            raise APIError("Transaction not found", 404)
        
        # Update transaction
        result = supabase.table("transactions")\
            .update(data)\
            .eq("id", str(transaction_id))\
            .execute()
            
        return jsonify(result.data[0]), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(str(e), 500)

@app.route("/transactions/<uuid:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id):
    try:
        # Check if transaction exists
        exists = supabase.table("transactions")\
            .select("id")\
            .eq("id", str(transaction_id))\
            .execute()
            
        if not exists.data:
            raise APIError("Transaction not found", 404)
        
        # Delete transaction
        result = supabase.table("transactions")\
            .delete()\
            .eq("id", str(transaction_id))\
            .execute()
            
        return "", 204
        
    except APIError as e:
        raise e
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
    app.run(debug=True)
