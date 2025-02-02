import gym
import numpy as np
import pandas as pd
from gym import spaces

from config import TRANSACTION_FEE_PERCENT
from risk_manager import RiskManager

class MultiAssetTradingEnv(gym.Env):
    """
    RL environment for multiple crypto assets.
    Observations:
      - For each asset, [close, ma_50, ma_200, rsi]
      - plus portfolio info: [net_worth, fraction_in_crypto]

    Actions:
      - For each asset, a fraction in [0,1] of total net worth to allocate.

    The environment steps through a pandas DataFrame row by row,
    simulating trades at each step.
    """

    def __init__(self, df: pd.DataFrame, product_ids, initial_balance=10000):
        super().__init__()
        # Store market data
        self.df = df.reset_index(drop=True)
        self.product_ids = product_ids
        self.n_assets = len(product_ids)
        self.initial_balance = float(initial_balance)

        # Each asset has 4 observation values: [close, ma_50, ma_200, rsi].
        # We add 2 more for [net_worth, fraction_in_crypto].
        self.obs_per_asset = 4
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.n_assets * self.obs_per_asset + 2,),
            dtype=np.float32
        )

        # Actions: for each asset, a fraction [0..1].
        self.action_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(self.n_assets,),
            dtype=np.float32
        )

        # Risk manager
        self.risk_manager = RiskManager()

        # Initialize
        self.reset()

    def reset(self):
        """
        Reset the environment state for a new episode.
        Returns the initial observation.
        """
        self.current_step = 0
        self.cash_balance = self.initial_balance
        # Float32 zeros to store how many "units" of each asset we hold
        self.asset_holdings = np.zeros(self.n_assets, dtype=np.float32)
        self.prev_net_worth = self.initial_balance

        # Return the first observation
        return self._get_observation()

    def _get_observation(self):
        """
        Build an observation vector containing:
          [close, ma_50, ma_200, rsi] for each asset
          plus [net_worth, fraction_in_crypto].
        """
        # Clamp step in case we are at the very end
        if self.current_step >= len(self.df):
            self.current_step = len(self.df) - 1

        row = self.df.loc[self.current_step]

        # Gather per-asset features
        obs = []
        for pid in self.product_ids:
            # Convert row values to float to avoid type errors
            close = float(row[f"{pid}_close"])
            ma50 = float(row[f"{pid}_ma_50"])
            ma200 = float(row[f"{pid}_ma_200"])
            rsi = float(row[f"{pid}_rsi"])
            obs.extend([close, ma50, ma200, rsi])

        # Portfolio info
        net_worth = self._calculate_net_worth(row)
        if net_worth > 0:
            fraction_in_crypto = 1.0 - (self.cash_balance / net_worth)
        else:
            fraction_in_crypto = 1.0

        obs.append(net_worth)
        obs.append(fraction_in_crypto)

        return np.array(obs, dtype=np.float32)

    def _calculate_net_worth(self, row):
        """
        net_worth = cash_balance + sum(asset_holdings[i] * close_price_i).
        """
        net = float(self.cash_balance)
        for i, pid in enumerate(self.product_ids):
            close_price = float(row[f"{pid}_close"])
            net += float(self.asset_holdings[i]) * close_price
        return net

    # Comment this out or redefine properly if needed
    # def calculate_total_value(self):
    #     cash = self.portfolio.cash  # But self.portfolio is not defined
    #     crypto_value = sum(
    #         position.amount * self.get_current_price(symbol)
    #         for symbol, position in self.portfolio.positions.items()
    #     )
    #     return cash + crypto_value

    def step(self, action):
        """
        action: array of target fractions [f1, f2, ..., fN] for each asset
                in [0,1].
        We'll rebalance to match these fractions of net worth at the
        *current* prices.
        """
        # 1) If we've run out of data, the episode is done
        if self.current_step >= len(self.df):
            # Provide a final observation (clamped)
            obs = self._get_observation()
            return obs, 0.0, True, {}

        # 2) Current row & net worth
        row = self.df.loc[self.current_step]
        current_net_worth = self._calculate_net_worth(row)

        # 3) Risk constraints
        action = self.risk_manager.apply_risk_constraints(
            action, self.asset_holdings, self.cash_balance, row, current_net_worth
        )

        # 4) Rebalance based on the new action
        desired_allocation = action  # fraction of net worth for each asset
        for i, pid in enumerate(self.product_ids):
            asset_price = float(row[f"{pid}_close"])
            target_value = current_net_worth * float(desired_allocation[i])
            current_value = float(self.asset_holdings[i]) * asset_price
            diff = target_value - current_value

            # Skip tiny differences
            if abs(diff) < 1e-8:
                continue

            # Transaction fee
            fee = abs(diff) * TRANSACTION_FEE_PERCENT

            if diff > 0:
                # Buy
                cost = diff + fee
                if cost <= self.cash_balance:
                    self.cash_balance -= cost
                    self.asset_holdings[i] += (diff / asset_price)
            else:
                # Sell
                self.cash_balance += (abs(diff) - fee)
                self.asset_holdings[i] -= (abs(diff) / asset_price)

        # 5) Advance step
        self.current_step += 1
        done = (self.current_step >= len(self.df))
        if done:
            # clamp step so _get_observation() won't fail
            self.current_step = len(self.df) - 1

        # 6) Calculate new net worth & reward
        new_row = self.df.loc[self.current_step] if not done else row
        new_net_worth = self._calculate_net_worth(new_row)
        reward = new_net_worth - current_net_worth

        # 7) Build next observation
        obs = self._get_observation()
        info = {"net_worth": new_net_worth}

        return obs, reward, done, info
