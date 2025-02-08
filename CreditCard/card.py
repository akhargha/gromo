# CreditCard.py
from current_balance import CurrentBalance
from cashback import Cashback
from transactions import Transactions

class CreditCard:
    def __init__(self, credit_limit: float):
        self.credit_limit = credit_limit
        self.current_balance = CurrentBalance()
        self.cashback = Cashback()
        self.transactions = Transactions()

    def process_transaction(self, amount: float, description: str) -> None:
        """
        Process a charge transaction.
        Checks for available credit before proceeding.
        :param amount: The charge amount.
        :param description: Description of the transaction.
        :raises Exception: if there is insufficient available credit.
        """
        if self.get_available_credit() >= amount:
            self.current_balance.debit(amount)
            self.transactions.add_transaction(amount, description)
            self.cashback.calculate_reward(amount)
            print(f"Processed transaction of ${amount}: {description}")
        else:
            raise Exception("Insufficient available credit")

    def get_available_credit(self) -> float:
        """
        Compute and return the available credit.
        :return: Credit limit minus current balance.
        """
        return self.credit_limit - self.current_balance.balance

    def make_payment(self, amount: float) -> None:
        """
        Apply a payment to reduce the current balance.
        :param amount: Payment amount.
        """
        self.current_balance.credit(amount)
        self.transactions.add_transaction(-amount, "Payment Received")
        print(f"Payment of ${amount} received.")

    def redeem_cashback(self) -> float:
        """
        Redeem and reset the accumulated cashback rewards.
        :return: The redeemed rewards amount.
        """
        redeemed = self.cashback.redeem_rewards()
        print(f"Redeemed ${redeemed} in rewards.")
        return redeemed

# Demo usage
if __name__ == '__main__':
    # Create a CreditCard instance with a $5,000 credit limit
    card = CreditCard(credit_limit=5000.0)
    print("Initial available credit: $", card.get_available_credit())

    # Process some transactions
    card.process_transaction(100, "Groceries")
    card.process_transaction(50, "Dining")

    print("Available credit after transactions: $", card.get_available_credit())

    # Make a payment
    card.make_payment(75)
    print("Available credit after payment: $", card.get_available_credit())

    # Redeem cashback rewards
    rewards = card.redeem_cashback()
    print("Cashback rewards redeemed: $", rewards)
