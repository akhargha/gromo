# transactions.py
from supabase import create_client, Client
import datetime

class Transactions:
    def __init__(self):
        """
        Initialize the Supabase client using hardcoded environment values.
        """
        self.supabase_url = "https://dicdnvswymiaugijpjfa.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRpY2RudnN3eW1pYXVnaWpwamZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwMzYzNDAsImV4cCI6MjA1NDYxMjM0MH0.piFtbs8TCzvYAl-5htYNcl-fdAYkoqJEeIaUDz_iCI4"
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def add_transaction(self, credit_card_id: int, cc_number: str, transaction_amount: float, description: str) -> dict:
        """
        Add a new transaction to the transactions table in Supabase.

        :param credit_card_id: The ID of the credit card (foreign key from credit_cards table).
        :param cc_number: The credit card number (redundant copy for convenience).
        :param transaction_amount: The amount of the transaction.
        :param description: A short description of the transaction.
        :return: The newly inserted transaction record as a dictionary.
        """
        transaction = {
            "credit_card_id": credit_card_id,
            "cc_number": cc_number,
            "transaction_amount": transaction_amount,
            "description": description,
            "transaction_date": datetime.datetime.now().isoformat()
        }
        response = self.client.table("transactions").insert(transaction).execute()
        # Return the first (and only) record inserted if available.
        return response.data[0] if response.data and len(response.data) > 0 else {}

    def get_all_transactions(self) -> list:
        """
        Fetch all transactions from the transactions table.

        :return: A list of transaction records as dictionaries.
        """
        response = self.client.table("transactions").select("*").order("transaction_date", desc=True).execute()
        return response.data if response.data else []

    def get_transaction_by_id(self, transaction_id: int) -> dict:
        """
        Retrieve a transaction record by its unique ID.

        :param transaction_id: The unique ID of the transaction.
        :return: A dictionary representing the transaction, or an empty dictionary if not found.
        """
        response = self.client.table("transactions").select("*").eq("id", transaction_id).execute()
        return response.data[0] if response.data and len(response.data) > 0 else {}

    def update_transaction(self, transaction_id: int, updates: dict) -> dict:
        """
        Update specific fields of a transaction record.

        :param transaction_id: The unique ID of the transaction to update.
        :param updates: A dictionary containing the fields to update (e.g., {"transaction_amount": 150.00}).
        :return: The updated transaction record as a dictionary.
        """
        response = self.client.table("transactions").update(updates).eq("id", transaction_id).execute()
        return response.data[0] if response.data and len(response.data) > 0 else {}

    def delete_transaction(self, transaction_id: int) -> dict:
        """
        Delete a transaction record by its unique ID.

        :param transaction_id: The unique ID of the transaction to delete.
        :return: The deleted transaction record as a dictionary.
        """
        response = self.client.table("transactions").delete().eq("id", transaction_id).execute()
        return response.data[0] if response.data and len(response.data) > 0 else {}

# Example usage (for testing purposes)
if __name__ == '__main__':
    transactions_obj = Transactions()

    # Add a transaction
    new_tx = transactions_obj.add_transaction(
        credit_card_id=1,
        cc_number="1234-5678-9012-3456",
        transaction_amount=100.00,
        description="Groceries Purchase"
    )
    print("Added Transaction:", new_tx)

    # Fetch all transactions
    all_transactions = transactions_obj.get_all_transactions()
    print("All Transactions:", all_transactions)

    # Fetch a specific transaction by ID (if exists)
    tx = transactions_obj.get_transaction_by_id(new_tx.get("id"))
    print("Fetched Transaction by ID:", tx)

    # Update the transaction (e.g., change the amount)
    updated_tx = transactions_obj.update_transaction(new_tx.get("id"), {"transaction_amount": 120.00})
    print("Updated Transaction:", updated_tx)
