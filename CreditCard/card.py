from flask import Flask, jsonify, request
from supabase import create_client, Client
import datetime

app = Flask(__name__)
PORT = 5001

# Supabase Credentials
SUPABASE_URL = "https://dicdnvswymiaugijpjfa.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRpY2RudnN3eW1pYXVnaWpwamZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwMzYzNDAsImV4cCI6MjA1NDYxMjM0MH0."
    "piFtbs8TCzvYAl-5htYNcl-fdAYkoqJEeIaUDz_iCI4"
)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_all_transactions():
    """Fetch all transactions from the transactions table."""
    response = supabase.table("transactions").select("*").execute()
    return response.data if response.data else []

def get_all_credit_cards():
    """Fetch all credit card details from the credit_cards table."""
    response = supabase.table("credit_cards").select("id", "credit_line").execute()
    return response.data if response.data else []

def update_credit_card(credit_card_id: int, updates: dict):
    """Update a credit card record in the credit_cards table."""
    response = supabase.table("credit_cards").update(updates).eq("id", credit_card_id).execute()
    return response.data[0] if response.data and len(response.data) > 0 else {}

def calculate_total_spent(credit_card_id: int):
    """Calculate the total amount spent for a given credit card."""
    response = supabase.table("transactions").select("transaction_amount").eq("credit_card_id", credit_card_id).execute()
    total_spent = sum(float(tx["transaction_amount"]) for tx in response.data) if response.data else 0
    return total_spent

@app.route("/update_credit_cards", methods=["GET"])
def update_credit_cards():
    """
    Update credit card records by:
     - Fetching all transactions.
     - Calculating new current balance, available credit, and rewards cash dynamically from the credit card table.
    """
    credit_cards = get_all_credit_cards()
    updated_records = []

    for card in credit_cards:
        credit_card_id = card["id"]
        credit_line = float(card["credit_line"])  # Get the credit line from the credit_cards table
        total_spent = calculate_total_spent(credit_card_id)
        cashback = total_spent * 0.03  # 3% cashback calculation
        
        current_balance = total_spent
        available_credit = credit_line - total_spent
        rewards_cash = cashback
        updated_at = datetime.datetime.now().isoformat()

        update_credit_card(credit_card_id, {
            "current_balance": current_balance,
            "available_credit": available_credit,
            "rewards_cash": rewards_cash,
            "updated_at": updated_at
        })
        updated_records.append({"credit_card_id": credit_card_id, "current_balance": current_balance, "available_credit": available_credit, "rewards_cash": rewards_cash})
    
    return jsonify({"message": "Credit card balances and rewards updated successfully", "records": updated_records})

@app.route("/get_credit_card_details/<int:credit_card_id>", methods=["GET"])
def get_credit_card_details_endpoint(credit_card_id):
    """Fetch and return details of a specific credit card."""
    response = supabase.table("credit_cards").select("*").eq("id", credit_card_id).execute()
    return jsonify(response.data[0] if response.data else {})

@app.route("/get_credit_cards", methods=["GET"])
def get_credit_cards():
    """Fetch and return all credit card details."""
    response = supabase.table("credit_cards").select("*").execute()
    return jsonify({"credit_cards": response.data if response.data else []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)