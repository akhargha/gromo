from flask import Flask, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/credit_card", methods=["GET"])
def get_credit_card():
    """Get the single credit card details."""
    response = supabase.table("credit_card").select("*").single().execute()

    # Ensure we are accessing the correct response format
    if "error" in response and response["error"]:
        return jsonify({"error": response["error"]["message"]}), 404

    # The data is usually inside the first index of the returned list
    if response.data:
        return jsonify(response.data)
    
    return jsonify({"error": "Credit card not found"}), 404

@app.route("/credit_card", methods=["PUT"])
def update_credit_card():
    """Update the single credit card details."""
    data = request.json
    update_data = {}
    for field in ["credit_limit", "available_credit", "curr_balance", "rewards_cash"]:
        if field in data:
            update_data[field] = data[field]
    
    response = supabase.table("credit_card").update(update_data).neq("id", None).execute()
    if response.get("error"):
        return jsonify({"error": "Failed to update credit card"}), 400
    return jsonify(response["data"]) 

if __name__ == "__main__":
    app.run(debug=True)
