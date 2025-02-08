# cashback.py
class Cashback:
    def __init__(self):
        self.rewards_cash = 0.0  # Accumulated cashback rewards

    def calculate_reward(self, amount: float) -> None:
        """
        Calculate and add cashback rewards from a transaction.
        For example, using a 3% reward rate.
        :param amount: The transaction amount.
        """
        reward = amount * 0.03
        self.rewards_cash += reward

    def redeem_rewards(self) -> float:
        """
        Redeem all accumulated rewards.
        :return: The redeemed rewards value.
        """
        redeemed_value = self.rewards_cash
        self.rewards_cash = 0.0
        return redeemed_value
