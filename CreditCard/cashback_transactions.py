from flask import Flask, jsonify
from supabase import create_client, Client
import datetime

app = Flask(__name__)
PORT = 5002

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

def get_cashback_transaction_by_transaction_id(transaction_id: int):
    """Retrieve a cashback transaction record based on transaction_id."""
    response = supabase.table("cashback_transactions").select("*").eq("transaction_id", transaction_id).execute()
    return response.data[0] if response.data and len(response.data) > 0 else {}

def add_cashback_transaction(transaction_id: int, cashback_amount: float):
    """Insert a new cashback transaction record."""
    record = {
        "transaction_id": transaction_id,
        "cashback_amount": cashback_amount,
        "computed_at": datetime.datetime.now().isoformat()
    }
    response = supabase.table("cashback_transactions").insert(record).execute()
    return response.data[0] if response.data and len(response.data) > 0 else {}

def update_cashback_transaction(cashback_transaction_id: int, updates: dict):
    """Update an existing cashback transaction record."""
    response = supabase.table("cashback_transactions").update(updates).eq("id", cashback_transaction_id).execute()
    return response.data[0] if response.data and len(response.data) > 0 else {}

@app.route("/sync_cashback_transactions", methods=["GET"])
def sync_cashback_transactions():
    """
    Sync cashback transactions by:
     - Fetching all transactions.
     - Calculating cashback (3% of transaction amount for positive amounts).
     - Checking if a cashback record exists and updating/inserting as needed.
    """
    transactions = get_all_transactions()
    updated_records = []

    for tx in transactions:
        tx_id = tx.get("id")
        try:
            amount = float(tx.get("transaction_amount", 0))
        except (TypeError, ValueError):
            continue

        cashback_amount = amount * 0.03 if amount > 0 else 0
        if tx_id is None:
            continue

        existing_record = get_cashback_transaction_by_transaction_id(tx_id)
        if existing_record:
            existing_cashback = float(existing_record.get("cashback_amount", 0))
            if abs(existing_cashback - cashback_amount) > 0.001:
                updates = {"cashback_amount": cashback_amount, "computed_at": datetime.datetime.now().isoformat()}
                update_cashback_transaction(existing_record["id"], updates)
                updated_records.append({"transaction_id": tx_id, "action": "updated", "cashback_amount": cashback_amount})
        else:
            if cashback_amount > 0:
                add_cashback_transaction(tx_id, cashback_amount)
                updated_records.append({"transaction_id": tx_id, "action": "added", "cashback_amount": cashback_amount})
    
    return jsonify({"message": "Cashback transactions synced successfully", "records": updated_records})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
