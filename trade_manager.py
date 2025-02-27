import math
from coinbase.rest import RESTClient
from config import COINBASE_API_KEY, COINBASE_API_SECRET

class CoinbaseClient:
    """
    A 'bridge' class that mimics older cbpro-like function calls
    but uses coinbase-advanced-py (RESTClient) underneath.
    """

    def __init__(self):
        self.client = RESTClient(
            api_key=COINBASE_API_KEY,
            api_secret=COINBASE_API_SECRET
        )

    def place_market_order(self, product_id: str, side: str, funds=None, size=None):
        """
        Create a market order using coinbase-advanced-py.
        - `funds` = USD amount (quote_size) to buy/sell
        - `size` = base units (e.g., BTC) to buy/sell
        """
        side = side.lower()
        if side not in ("buy", "sell"):
            return {"error": "Invalid side. Must be 'buy' or 'sell'."}

        if funds is None and size is None:
            return {"error": "Either 'funds' (USD) or 'size' (base units) must be provided."}

        client_order_id = ""
        try:
            if side == "buy":
                if funds is not None:
                    resp = self.client.market_order_buy(
                        client_order_id=client_order_id,
                        product_id=product_id,
                        quote_size=str(funds)
                    )
                else:  # using base `size`
                    resp = self.client.market_order_buy(
                        client_order_id=client_order_id,
                        product_id=product_id,
                        base_size=str(size)
                    )
            else:  # side == "sell"
                if funds is not None:
                    resp = self.client.market_order_sell(
                        client_order_id=client_order_id,
                        product_id=product_id,
                        quote_size=str(funds)
                    )
                else:
                    resp = self.client.market_order_sell(
                        client_order_id=client_order_id,
                        product_id=product_id,
                        base_size=str(size)
                    )
            return resp.to_dict()
        except Exception as e:
            return {"error": str(e)}

    def place_limit_order(self, product_id: str, side: str, limit_price, size):
        """
        Example bridging for a limit order. Buys/sells a certain 'base_size'
        at `limit_price`.
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
                    base_size=base_size_str
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
        Return account balances in a list of dicts.
        """
        results = []
        try:
            accounts = self.client.get_accounts()
            for acct in accounts.accounts:
                if not acct.available_balance:
                    continue
                currency = acct.available_balance["currency"]
                balance_value = acct.available_balance["value"]
                results.append({"currency": currency, "balance": balance_value})
        except Exception as e:
            return [{"error": str(e)}]
        return results

    def get_current_price(self, product_id="BTC-USD"):
        """
        Approximate 'current price' by averaging the top bid and ask.
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

    def get_open_orders(self, product_id=None):
        """
        Fetch all open orders (optionally filtered by product_id).
        """
        try:
            # coinbase-advanced-py docs: list_orders(order_status=["OPEN"], ...)
            open_orders = self.client.list_orders(
                limit=100,
                order_status=["OPEN"],
                product_id=product_id or ""
            )
            return [order.to_dict() for order in open_orders.orders]
        except Exception as e:
            return {"error": str(e)}


class TradingBot:
    """
    A simple wrapper around CoinbaseClient that implements
    high-level 'execute_trade' and 'get_active_trades' methods.
    """

    def __init__(self):
        self.client = CoinbaseClient()

    def execute_trade(self, symbol: str, side: str, quantity: float):
        """
        Executes a market trade using `quantity` as the USD 'funds'
        for simplicity. If you need base units, pass `size=quantity`
        instead and set `funds=None`.
        """
        # Example: Use quantity as 'funds' in USD
        response = self.client.place_market_order(
            product_id=symbol,
            side=side,
            funds=quantity  # or `size=quantity` if you prefer base units
        )
        return response

    def get_active_trades(self, symbol=None):
        """
        Return open (active) orders from Coinbase. Optionally filter by symbol.
        """
        return self.client.get_open_orders(product_id=symbol)
