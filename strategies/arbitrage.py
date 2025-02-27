# ai_trader/strategies/arbitrage.py
from .base_strategy import Strategy

class ArbitrageStrategy(Strategy):
    def generate_signals(self, market_data):
        signals = []
        for pair in market_data:
            prices = {exchange: data['price'] for exchange, data in market_data[pair].items()}
            min_price = min(prices.values())
            max_price = max(prices.values())
            if (max_price - min_price) > 0.01:  # Threshold for profit after fees
                signals.append({
                    'pair': pair,
                    'buy_exchange': min(prices, key=prices.get),
                    'sell_exchange': max(prices, key=prices.get),
                    'profit': max_price - min_price
                })
        return signals

    def execute_trades(self, signals, exchange_clients):
        for signal in signals:
            buy_client = exchange_clients[signal['buy_exchange']]
            sell_client = exchange_clients[signal['sell_exchange']]
            buy_client.place_order(signal['pair'], 'buy', signal['profit'] / 2)
            sell_client.place_order(signal['pair'], 'sell', signal['profit'] / 2)