# transactions.py
class Transactions:
    def __init__(self):
        self.history = []  # List to store transaction records

    def add_transaction(self, amount: float, description: str) -> None:
        """
        Add a new transaction to the history.
        :param amount: The amount for the transaction.
        :param description: A short description of the transaction.
        """
        transaction = {
            "amount": amount,
            "description": description,
            # Optionally add more details like a timestamp, e.g., datetime.now()
        }
        self.history.append(transaction)
