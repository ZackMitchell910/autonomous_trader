# trade_manager.py

import math
from coinbase.rest import RESTClient
from config import COINBASE_API_KEY, COINBASE_API_SECRET

class CoinbaseClient:
    """
    A 'bridge' class that mimics older cbpro-like function calls but uses
    the official Coinbase Advanced Python SDK (coinbase-advanced-py) underneath.
    """

    def __init__(self):
        """
        Initialize the RESTClient from coinbase-advanced-py using your
        Advanced Trade API Key + Secret (Cloud Developer Platform keys).
        """
        self.client = RESTClient(
            api_key=COINBASE_API_KEY,
            api_secret=COINBASE_API_SECRET
        )

    def place_market_order(self, product_id: str, side: str, funds=None, size=None):
        """
        Mimics the old cbpro signature:
          - product_id = e.g. "BTC-USD"
          - side = "buy" or "sell"
          - funds = how many USD to spend (for a buy/sell in quote currency)
          - size = how many base units to buy/sell (not currently used in this example)

        Under the hood, calls `market_order_buy` or `market_order_sell` from coinbase-advanced-py.

        NOTE: The official library’s market_order_* methods expect:
          - `quote_size`: str, how many quote units (USD) to buy/sell
          - or `base_size`: str, how many base units (e.g., BTC).
        Here, we assume a "buy" or "sell" in terms of USD. If you want to trade by base units,
        adapt accordingly.
        """
        side = side.lower()
        if side not in ("buy", "sell"):
            return {"error": "Invalid side. Must be 'buy' or 'sell'."}

        if funds is None:
            return {"error": "This example expects a 'funds' USD amount (quote_size) to trade."}

        # Convert numeric funds to string for the official SDK
        quote_size_str = str(funds)

        # Use an empty string or unique ID for client_order_id
        # to avoid accidental duplicate orders.
        client_order_id = ""

        try:
            if side == "buy":
                resp = self.client.market_order_buy(
                    client_order_id=client_order_id,
                    product_id=product_id,
                    quote_size=quote_size_str
                )
            else:  # side == "sell"
                resp = self.client.market_order_sell(
                    client_order_id=client_order_id,
                    product_id=product_id,
                    quote_size=quote_size_str
                )
            return resp.to_dict()  # Convert protobuf response to a Python dict
        except Exception as e:
            return {"error": str(e)}

    def place_limit_order(self, product_id: str, side: str, limit_price, size):
        """
        Example bridging for a limit order. The official library has:
          - limit_order_buy(...)
          - limit_order_sell(...)
        expecting either a base_size or quote_size.

        Here, we show a minimal approach to buy or sell a certain 'base_size' at a limit_price.
        If you prefer specifying quote size in USD, adapt accordingly.

        :param product_id: e.g. "BTC-USD"
        :param side: "buy" or "sell"
        :param limit_price: The price at which to trigger the buy/sell (string or float)
        :param size: The number of base units (e.g. BTC) you want to trade
        """
        side = side.lower()
        if side not in ("buy", "sell"):
            return {"error": "Invalid side. Must be 'buy' or 'sell'."}

        try:
            limit_price_str = str(limit_price)
            base_size_str = str(size)
            client_order_id = ""

            if side == "buy":
                resp = self.client.limit_order_buy(
                    client_order_id=client_order_id,
                    product_id=product_id,
                    limit_price=limit_price_str,
                    base_size=base_size_str,
                    # other params like time_in_force, post_only, etc. can go here
                )
            else:  # side == "sell"
                resp = self.client.limit_order_sell(
                    client_order_id=client_order_id,
                    product_id=product_id,
                    limit_price=limit_price_str,
                    base_size=base_size_str
                )
            return resp.to_dict()
        except Exception as e:
            return {"error": str(e)}

    def get_account_balances(self):
        """
        Return account balances in a list of dicts, like:
          [
            {"currency": "BTC", "balance": "0.02"},
            {"currency": "USD", "balance": "500.0"},
            ...
          ]

        Uses the official method get_accounts(). Each Account object has
        available_balance, which is a dict with {"value": "...", "currency": "..."}.
        """
        results = []
        try:
            accounts = self.client.get_accounts()
            # 'accounts.accounts' is a list of Account objects
            for acct in accounts.accounts:
                # 'available_balance' is a dict like {"value": "...", "currency": "..."}
                if not acct.available_balance:
                    # Some accounts may have no available_balance field
                    continue
                currency = acct.available_balance["currency"]
                balance_value = acct.available_balance["value"]
                results.append({"currency": currency, "balance": balance_value})
        except Exception as e:
            return [{"error": str(e)}]

        return results

    def get_current_price(self, product_id="BTC-USD"):
        """
        Approximate a 'current price' by fetching the level-1 order book (top of book),
        taking best bid and best ask, then averaging.

        The official library’s get_product_order_book() returns an OrderBook
        with arrays of bids and asks. Each 'bid' or 'ask' has the form:
           price: "...", size: "...", num_orders: ...
        """
        try:
            order_book = self.client.get_product_order_book(product_id=product_id, level=1)
            if not order_book.bids or not order_book.asks:
                return {"error": "No bids or asks returned."}

            best_bid = float(order_book.bids[0].price)
            best_ask = float(order_book.asks[0].price)
            mid_price = (best_bid + best_ask) / 2.0
            return mid_price
        except Exception as e:
            return {"error": str(e)}
