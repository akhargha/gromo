# current_balance.py
class CurrentBalance:
    def __init__(self):
        self.balance = 0.0  # Total outstanding balance

    def debit(self, amount: float) -> None:
        """
        Increase balance due to a charge.
        :param amount: The charge amount to add.
        """
        self.balance += amount

    def credit(self, amount: float) -> None:
        """
        Decrease balance due to a payment.
        :param amount: The payment amount to subtract.
        """
        self.balance -= amount
