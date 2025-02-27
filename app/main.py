from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Dict
import jwt

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

users = {}  # In-memory store for demo; use database in production

@app.post("/add_exchange")
async def add_exchange(config: ExchangeConfig, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    limits = {1: 1, 2: 2, 3: 5}
    if len(user.exchanges) >= limits.get(user.tier, 0):
        raise HTTPException(status_code=403, detail="Exchange limit reached")
    user.exchanges.append(config)
    return {"message": "Exchange added"}

def get_current_user(token: str):
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        return users.get(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")