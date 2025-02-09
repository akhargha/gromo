import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# -----------------------------------------------------------------------------
# 1. Supabase Configuration
# -----------------------------------------------------------------------------


# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("REACT_APP_SUPABASE_URL"),
    os.getenv("REACT_APP_SUPABASE_ANON_KEY")
)

# -----------------------------------------------------------------------------
# 2. Health Check
# -----------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# -----------------------------------------------------------------------------
# 3. Get the Single Credit Card Row
#    GET /credit_card
# -----------------------------------------------------------------------------
@app.route("/credit_card", methods=["GET"])
def get_credit_card():
    """
    Since there's always exactly one row, we can simply fetch it with .single().
    For new supabase-py versions, check status_code instead of response.error.
    """
    try:
        response = supabase.table("credit_card").select("*").execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# 4. Update the Single Credit Card Row
#    PUT /credit_card
#    Expects JSON with any of the fields:
#       {
#         "credit_limit": <numeric>,
#         "available_credit": <numeric>,
#         "curr_balance": <numeric>,
#         "rewards_cash": <numeric>
#       }
# -----------------------------------------------------------------------------
@app.route("/credit_card", methods=["PUT"])
def update_credit_card():
    """
    Updates the single credit_card row. We don’t need to filter by ID since
    only one row exists in the table.
    """
    try:
        data = request.get_json()

        # Only include valid fields
        valid_keys = ["credit_limit", "available_credit", "curr_balance", "rewards_cash"]
        update_data = {k: v for k, v in data.items() if k in valid_keys}

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        # Update the single row
        response = supabase.table("credit_card").update(update_data).eq("credit_limit", 10000).execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# 5. Run the Flask App
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
