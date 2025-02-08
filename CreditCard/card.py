# CreditCard.py
from current_balance import CurrentBalance
from cashback import Cashback
from transactions import Transactions
import datetime
from supabase import create_client, Client

class CreditCard:
    def __init__(self, credit_card_id: int, credit_limit: float, cc_number: str):
        """
        Initialize the CreditCard instance and connect to Supabase.
        :param credit_card_id: The ID of the credit card record in the credit_cards table.
        :param credit_limit: The total credit limit for the card.
        :param cc_number: The credit card number.
        """
        self.credit_card_id = credit_card_id
        self.cc_number = cc_number
        self.credit_limit = credit_limit
        self.current_balance = CurrentBalance()
        self.cashback = Cashback()
        self.transactions = Transactions()

        # Initialize Supabase client for updating the credit_cards table
        self.supabase_url = "https://dicdnvswymiaugijpjfa.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRpY2RudnN3eW1pYXVnaWpwamZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwMzYzNDAsImV4cCI6MjA1NDYxMjM0MH0.piFtbs8TCzvYAl-5htYNcl-fdAYkoqJEeIaUDz_iCI4"
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def update_credit_card_record(self):
        """
        Update the credit card record in the credit_cards table to reflect the latest
        current_balance, available_credit, and rewards_cash.
        """
        record = {
            "current_balance": self.current_balance.balance,
            "available_credit": self.get_available_credit(),
            "rewards_cash": self.cashback.rewards_cash,
            "updated_at": datetime.datetime.now().isoformat()
        }
        response = self.client.table("credit_cards").update(record).eq("id", self.credit_card_id).execute()
        return response.data

    def get_available_credit(self) -> float:
        """
        Compute and return the available credit.
        :return: Credit limit minus current balance.
        """
        return self.credit_limit - self.current_balance.balance

    def sync_account(self) -> None:
        """
        Sync the credit card account by:
         - Fetching all transactions (via the Transactions class),
         - Filtering them by this card's credit_card_id,
         - Aggregating the current balance (as the sum of all transaction_amount values),
         - Computing the cashback (3% of all positive transactions),
         - And updating the credit_cards record in Supabase.
        """
        # Fetch all transactions from the transactions table
        all_transactions = self.transactions.get_all_transactions()
        # Filter transactions to those matching this credit card
        transactions = [
            tx for tx in all_transactions
            if int(tx.get("credit_card_id", 0)) == self.credit_card_id
        ]
        
        # Aggregate the current balance: sum all transaction_amount values.
        computed_balance = sum(float(tx.get("transaction_amount", 0)) for tx in transactions)
        
        # Aggregate cashback: assume cashback is 3% of all positive (charge) transactions.
        computed_cashback = sum(
            float(tx.get("transaction_amount", 0)) * 0.03
            for tx in transactions if float(tx.get("transaction_amount", 0)) > 0
        )
        
        # Update internal state
        self.current_balance.balance = computed_balance
        self.cashback.rewards_cash = computed_cashback
        
        # Update the credit_cards record in Supabase
        self.update_credit_card_record()
        print(f"Synced account: Current Balance = ${computed_balance}, Rewards Cash = ${computed_cashback}")

# Demo usage
if __name__ == '__main__':
    # For demonstration purposes, assume:
    # credit_card_id=1, a $5,000 credit limit, and a given card number.
    card = CreditCard(credit_card_id=1, credit_limit=5000.0, cc_number="1234-5678-9012-3456")
    
    # Instead of processing new transactions here,
    # sync the account by fetching existing transactions from Supabase
    # and updating the credit card details accordingly.
    card.sync_account()
