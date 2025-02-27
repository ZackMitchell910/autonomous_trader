from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from trade_manager import TradingBot

app = FastAPI()

# Initialize the Trading Bot
trading_bot = TradingBot()

# Health Check
@app.get("/health")
def health_check():
    return {"status": "Trading bot is running"}

# Schema for trade requests
class TradeRequest(BaseModel):
    symbol: str   # e.g. "BTC-USD"
    side: str     # "buy" or "sell"
    quantity: float  # in USD if using 'funds'

# Execute a market trade
@app.post("/trade")
def place_trade(trade: TradeRequest):
    try:
        result = trading_bot.execute_trade(
            symbol=trade.symbol,
            side=trade.side,
            quantity=trade.quantity
        )
        return {"message": "Trade executed", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get open orders
@app.get("/trades")
def get_open_trades(symbol: str = None):
    """
    Optional: pass ?symbol=BTC-USD to filter by product ID.
    """
    try:
        trades = trading_bot.get_active_trades(symbol=symbol)
        return {"open_trades": trades}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with `python -m uvicorn api:app --reload`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
