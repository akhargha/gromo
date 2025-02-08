# cashback_transactions.py
from supabase import create_client, Client
import datetime
from transactions import Transactions  # Import the Transactions class to fetch transaction records

class CashbackTransactions:
    def __init__(self):
        """
        Initialize the Supabase client for the cashback_transactions table using hardcoded environment values.
        """
        self.supabase_url = "https://dicdnvswymiaugijpjfa.supabase.co"
        self.supabase_key = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRpY2RudnN3eW1pYXVnaWpwamZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwMzYzNDAsImV4cCI6MjA1NDYxMjM0MH0."
            "piFtbs8TCzvYAl-5htYNcl-fdAYkoqJEeIaUDz_iCI4"
        )
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        # Instantiate the Transactions class to fetch transaction data.
        self.tx_obj = Transactions()

    def add_cashback_transaction(self, transaction_id: int, cashback_amount: float, transaction_amount: float) -> dict:
        """
        Add a new cashback transaction record to the cashback_transactions table.
        This method is used by sync_cashback_transactions when no record exists.
        
        :param transaction_id: The ID of the related transaction (foreign key from the transactions table).
        :param cashback_amount: The calculated cashback amount for the transaction.
        :param transaction_amount: The original transaction amount.
        :return: The newly inserted cashback transaction record as a dictionary.
        """
        record = {
            "transaction_id": transaction_id,
            "cashback_amount": cashback_amount,
            "transaction_amount": transaction_amount,
            "computed_at": datetime.datetime.now().isoformat()
        }
        response = self.client.table("cashback_transactions").insert(record).execute()
        return response.data[0] if response.data and len(response.data) > 0 else {}

    def update_cashback_transaction(self, cashback_transaction_id: int, updates: dict) -> dict:
        """
        Update specific fields of a cashback transaction record.
        
        :param cashback_transaction_id: The ID of the cashback transaction to update.
        :param updates: A dictionary of fields to update (e.g., {"cashback_amount": 4.50, "transaction_amount": 100.00}).
        :return: The updated cashback transaction record as a dictionary.
        """
        response = self.client.table("cashback_transactions").update(updates).eq("id", cashback_transaction_id).execute()
        return response.data[0] if response.data and len(response.data) > 0 else {}

    def get_cashback_transactions(self) -> list:
        """
        Fetch all cashback transactions from the cashback_transactions table.
        
        :return: A list of cashback transaction records as dictionaries.
        """
        response = self.client.table("cashback_transactions").select("*").order("computed_at", desc=True).execute()
        return response.data if response.data else []

    def get_cashback_transaction_by_transaction_id(self, transaction_id: int) -> dict:
        """
        Retrieve a cashback transaction record based on its associated transaction_id.
        
        :param transaction_id: The ID of the transaction.
        :return: The cashback transaction record as a dictionary, or an empty dictionary if not found.
        """
        response = self.client.table("cashback_transactions").select("*").eq("transaction_id", transaction_id).execute()
        return response.data[0] if response.data and len(response.data) > 0 else {}

    def sync_cashback_transactions(self) -> None:
        """
        Sync the cashback transactions by:
         - Fetching all transactions using the Transactions class.
         - For each transaction, calculate the cashback (3% of the transaction amount, only for positive amounts).
         - Check if a cashback record for that transaction exists:
             - If it exists and the cashback amount or transaction amount differs, update it.
             - If it does not exist and the cashback amount is positive, add a new record.
        """
        # Fetch all transactions from the transactions table.
        all_transactions = self.tx_obj.get_all_transactions()
        
        for tx in all_transactions:
            tx_id = tx.get("id")
            try:
                amount = float(tx.get("transaction_amount", 0))
            except (TypeError, ValueError):
                continue
            
            # Only consider positive transaction amounts for cashback.
            cashback_amount = amount * 0.03 if amount > 0 else 0
            if tx_id is None:
                continue
            
            existing_record = self.get_cashback_transaction_by_transaction_id(tx_id)
            if existing_record:
                existing_cashback = float(existing_record.get("cashback_amount", 0))
                existing_tx_amount = float(existing_record.get("transaction_amount", 0))
                # Update if either cashback or the original transaction amount differ significantly.
                if abs(existing_cashback - cashback_amount) > 0.001 or abs(existing_tx_amount - amount) > 0.001:
                    updates = {
                        "cashback_amount": cashback_amount,
                        "transaction_amount": amount,
                        "computed_at": datetime.datetime.now().isoformat()
                    }
                    self.update_cashback_transaction(existing_record["id"], updates)
                    print(f"Updated cashback for transaction {tx_id}: cashback {cashback_amount}, transaction_amount {amount}")
                else:
                    print(f"No update needed for transaction {tx_id}")
            else:
                if cashback_amount > 0:
                    self.add_cashback_transaction(tx_id, cashback_amount, amount)
                    print(f"Added cashback record for transaction {tx_id}: cashback {cashback_amount}, transaction_amount {amount}")

# Demo usage
if __name__ == '__main__':
    cashback_tx = CashbackTransactions()
    
    # Instead of manually adding a cashback record, sync cashback transactions based on existing transactions.
    cashback_tx.sync_cashback_transactions()
    
    # Optionally, fetch and print all cashback transactions after syncing.
    all_cashback = cashback_tx.get_cashback_transactions()
    print("All Cashback Transactions:", all_cashback)
