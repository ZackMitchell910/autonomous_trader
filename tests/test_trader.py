# tests/test_trader.py
def test_arbitrage():
    user = User(wallet_public_key="test", token_balance=40000000, tier=3)
    user.exchanges = [ExchangeConfig(exchange_name="binance", api_key="test_key", api_secret="test_secret")]
    settings = {"strategy": "arbitrage"}
    clients = initialize_exchanges(user.exchanges, test_mode=True)
    # Simulate market data and assert trades