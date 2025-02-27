# models/user.py
from pydantic import BaseModel
from typing import List, Dict

class ExchangeConfig(BaseModel):
    exchange_name: str
    api_key: str
    api_secret: str

class User(BaseModel):
    wallet_public_key: str
    token_balance: float
    tier: int
    exchanges: List[ExchangeConfig] = []
    settings: Dict = {}