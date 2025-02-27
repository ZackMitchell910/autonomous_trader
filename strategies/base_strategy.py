# ai_trader/strategies/base_strategy.py
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, market_data):
        """Generate trading signals based on market data."""
        pass

    @abstractmethod
    def execute_trades(self, signals, exchange_clients):
        """Execute trades based on generated signals."""
        pass