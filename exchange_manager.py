# ai_trader/exchange_manager.py
class ExchangeManager:
    def __init__(self, clients):
        self.clients = clients
        self.rate_limits = {e: {'calls': 0, 'limit': 100} for e in clients}

    def can_call(self, exchange):
        return self.rate_limits[exchange]['calls'] < self.rate_limits[exchange]['limit']

    def make_call(self, exchange, method, *args):
        if self.can_call(exchange):
            self.rate_limits[exchange]['calls'] += 1
            return getattr(self.clients[exchange], method)(*args)
        # Queue or delay