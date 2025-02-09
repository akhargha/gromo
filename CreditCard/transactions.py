from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import datetime

app = Flask(__name__)
CORS(app)

PORT = 5006

class Transactions:
    def __init__(self):
        self.supabase_url = "https://dicdnvswymiaugijpjfa.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRpY2RudnN3eW1pYXVnaWpwamZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwMzYzNDAsImV4cCI6MjA1NDYxMjM0MH0.piFtbs8TCzvYAl-5htYNcl-fdAYkoqJEeIaUDz_iCI4"
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def add_transaction(self, credit_card_id, cc_number, transaction_amount, description):
        transaction = {
            "credit_card_id": credit_card_id,
            "cc_number": cc_number,
            "transaction_amount": transaction_amount,
            "description": description,
            "transaction_date": datetime.datetime.now().isoformat()
        }
        response = self.client.table("transactions").insert(transaction).execute()
        return response.data[0] if response.data else {}

    def get_all_transactions(self):
        response = self.client.table("transactions").select("*").order("transaction_date", desc=True).execute()
        return response.data if response.data else []

    def get_transaction_by_id(self, transaction_id):
        response = self.client.table("transactions").select("*").eq("id", transaction_id).execute()
        return response.data[0] if response.data else {}

    def update_transaction(self, transaction_id, updates):
        response = self.client.table("transactions").update(updates).eq("id", transaction_id).execute()
        return response.data[0] if response.data else {}

    def delete_transaction(self, transaction_id):
        response = self.client.table("transactions").delete().eq("id", transaction_id).execute()
        return response.data[0] if response.data else {}

transactions_obj = Transactions()

@app.route('/transactions', methods=['GET'])
def get_transactions():
    return jsonify(transactions_obj.get_all_transactions())

@app.route('/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    return jsonify(transactions_obj.get_transaction_by_id(transaction_id))

@app.route('/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    new_transaction = transactions_obj.add_transaction(
        data['credit_card_id'], data['cc_number'], data['transaction_amount'], data['description']
    )
    return jsonify(new_transaction)

@app.route('/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    data = request.json
    updated_transaction = transactions_obj.update_transaction(transaction_id, data)
    return jsonify(updated_transaction)

@app.route('/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    deleted_transaction = transactions_obj.delete_transaction(transaction_id)
    return jsonify(deleted_transaction)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, debug=True)
