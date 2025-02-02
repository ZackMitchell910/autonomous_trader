import numpy as np
from config import MAX_POSITION_PERCENT, MAX_DRAWDOWN_PERCENT

class RiskManager:
    def __init__(self):
        self.peak_net_worth = None

    def apply_risk_constraints(self, action, asset_holdings, cash_balance, row, current_net_worth):
        """
        1. Ensure no single position > MAX_POSITION_PERCENT of net worth.
        2. If drawdown > MAX_DRAWDOWN_PERCENT, reduce risk drastically (e.g., go mostly to cash).
        """
        if self.peak_net_worth is None:
            self.peak_net_worth = current_net_worth
        else:
            self.peak_net_worth = max(self.peak_net_worth, current_net_worth)

        dd = 1 - (current_net_worth / self.peak_net_worth)
        if dd > MAX_DRAWDOWN_PERCENT:
            # Force mostly cash
            new_action = np.zeros_like(action)
            # perhaps leave a small fraction in stable allocations
            return new_action

        # If not in a drawdown, just ensure no single fraction > MAX_POSITION_PERCENT
        new_action = np.minimum(action, MAX_POSITION_PERCENT)
        sum_action = np.sum(new_action)
        if sum_action > 1.0:
            # scale down proportionally
            new_action = new_action / sum_action

        return new_action
