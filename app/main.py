# app/main.py
from fastapi import FastAPI, Depends
from models.user import User
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/trading_history")
@limiter.limit("100/minute")
async def get_trading_history(request: Request, user: User = Depends(get_current_user)):
    return {"history": user.trading_history}

app = FastAPI()

@app.post("/set_parameters")
async def set_parameters(settings: dict, user: User = Depends(get_current_user)):
    user.settings.update(settings)
    # Save to database
    return {"message": "Settings updated"}

    # app/main.py
@app.post("/add_exchange")
async def add_exchange(config: ExchangeConfig, user: User = Depends(get_current_user)):
    limits = {1: 1, 2: 2, 3: 5}  # Tier: max exchanges
    if len(user.exchanges) >= limits[user.tier]:
        raise HTTPException(status_code=403, detail="Exchange limit reached")
    config.api_key = encrypt_api_key(config.api_key)
    config.api_secret = encrypt_api_key(config.api_secret)
    user.exchanges.append(config)
    # Save to database
    return {"message": "Exchange added"}
    # app/main.py
@app.post("/start_trader")
async def start_trader(settings: dict, user: User = Depends(get_current_user)):
    # Start Celery task (see Step 4)
    task = run_trader.delay(user.dict(), settings)
    return {"task_id": task.id}

@app.get("/trading_history")
async def get_trading_history(user: User = Depends(get_current_user)):
    # Fetch from database
    return {"history": user.trading_history}
    # app/main.py
