import threading
import time
import queue
import pandas as pd
import requests, time, hmac, hashlib
import numpy as np

from config import (
    MODEL_SAVE_PATH,
    TRAIN_TIMESTEPS,
    ADMIN_CHAT_ID,
    SENTIMENT_THRESHOLD,
    RL_ALGO
)
from data_manager import DataManager
from ml_engine import MLEngine
from trade_manager import CoinbaseClient
from bot import main_bot
from utils import send_telegram_message
from sentiment_manager import SentimentManager
from x_scraper import start_twitter_stream
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

def tweet_consumer_loop(tweet_queue, sentiment_manager):
    """
    Continuously consumes tweets from the queue and feeds them to SentimentManager.
    """
    while True:
        try:
            tweet_text = tweet_queue.get(block=True, timeout=1)
            if tweet_text:
                sentiment_manager.add_tweet(tweet_text)
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error in tweet_consumer_loop: {e}")
        time.sleep(0.1)

def ai_trading_loop(model, product_ids, sentiment_manager):
    coinbase_client = CoinbaseClient()
    data_manager = DataManager(product_ids=product_ids)

    while True:
        try:
            sentiment_score = sentiment_manager.get_market_sentiment()
            if sentiment_score < 1 - SENTIMENT_THRESHOLD:
                msg = f"[AI] X sentiment is bearish ({sentiment_score:.2f}). Sitting on stables buying dips."
                send_telegram_message(ADMIN_CHAT_ID, msg)
                time.sleep(300)
                continue

            balances = coinbase_client.get_account_balances()
            if isinstance(balances, dict) and "error" in balances:
                # Something went wrong
                time.sleep(60)
                continue

            total_usd_value = 0.0
            usd_balance = 0.0
            coin_positions = {}

            for b in balances:
                currency = b["currency"]
                amount = float(b["balance"])
                if amount <= 0:
                    continue
                if currency == "USD":
                    usd_balance += amount 
                    total_usd_value += amount
                else:
                    pid = f"{currency}-USD"
                    if pid in product_ids:
                        coin_positions[currency] = amount

            end = pd.Timestamp.utcnow()
            start = end - pd.Timedelta("3 days")
            df_live = data_manager.build_multiasset_dataset(start, end)
            if df_live is None or df_live.empty:
                time.sleep(60)
                continue

            latest_row = df_live.iloc[-1]

            # 4) For each product, add to total_usd_value
            #    using the latest close to value them
            for currency, amount in coin_positions.items():
                pid = f"{currency}-USD"
                current_px = float(latest_row.get(f"{pid}_close", 0))
                total_usd_value += amount * current_px

            # 5) Build observation vector (obs)
            obs = []
            for pid in product_ids:
                obs.extend([
                    float(latest_row[f"{pid}_close"]),
                    float(latest_row[f"{pid}_ma_50"]),
                    float(latest_row[f"{pid}_ma_200"]),
                    float(latest_row[f"{pid}_rsi"])
                ])

            # Add mock net_worth & fraction_in_crypto, etc.
            fraction_in_crypto = 0.0
            if total_usd_value > 0:
                fraction_in_crypto = (total_usd_value - usd_balance) / total_usd_value

            obs.extend([
                total_usd_value,
                fraction_in_crypto,
                #usd_balance
            ])

            # Convert obs to the correct shape for model.predict
            obs_array = np.array(obs, dtype=np.float32).reshape(1, -1)

            # 6) Predict action from the RL model
            action, _states = model.predict(obs_array, deterministic=True)

            # If your action is multi-dimensional:
            if len(action.shape) > 1:
                action = action[0]

            # Filter out very small positions (avoid micro trades)
            action = np.where(np.abs(action) < 0.01, 0, action).astype(np.float32)

            # 7) Rebalance accordingly
            for i, pid in enumerate(product_ids):
                currency = pid.split("-")[0]
                current_px = float(latest_row[f"{pid}_close"])
                target_value = float(total_usd_value) * float(action[i])

                # Current value of the coin position
                current_value = 0.0
                if currency in coin_positions:
                    current_value = coin_positions[currency] * current_px

                diff = target_value - current_value
                # If the difference is tiny, skip
                if abs(diff) < 1.0:
                    continue

                try:
                    if diff > 0:
                        # Buy
                        buy_usd = diff * 0.5
                        # Avoid minuscule trades
                        if buy_usd < 5.0:
                            continue
                        res = coinbase_client.place_market_order(pid, "buy", funds=round(buy_usd, 2))
                        msg = f"[AI] Buying {currency} with ${buy_usd:.2f} (target: {action[i]*100:.1f}%)"
                    else:
                        # Sell
                        sell_amount = (abs(diff) * 0.5) / current_px
                        if sell_amount < 0.0001:
                            continue
                        res = coinbase_client.place_market_order(pid, "sell", size=round(sell_amount, 6))
                        msg = f"[AI] Selling {sell_amount:.6f} {currency} (target: {action[i]*100:.1f}%)"

                    send_telegram_message(ADMIN_CHAT_ID, msg + f" [Sentiment: {sentiment_score:.2f}]")

                except Exception as e:  # fix the spelling here
                    print(f"Error in processing {currency}: {e}")
                    continue

            # Sleep
            time.sleep(300)  # Wait 5 min

        except Exception as e:
            print(f"Error in AI trading loop: {e}")
            time.sleep(60)
            continue



def main():
    product_ids = ["BTC-USD", "TRUMP-USD", "ETH-USD", "SOL-USD"]

    # 1) Prepare training data for RL model
    dm = DataManager(product_ids=product_ids)
    end = pd.Timestamp.utcnow()
    start = end - pd.Timedelta("7 days")

    df = dm.build_multiasset_dataset(start, end)
    if df is None or df.empty:
        print("No historical data found. Exiting.")
        return

    # 2) Train or Load RL model
    ml_engine = MLEngine(df, product_ids, MODEL_SAVE_PATH, algo=RL_ALGO)
    # Uncomment to retrain model if needed:
    #model = ml_engine.train_model(timesteps=TRAIN_TIMESTEPS)
    model = ml_engine.load_model()

    # 3) Create Sentiment Manager
    sentiment_manager = SentimentManager()

    # 4) Start real-time X (Twitter) streaming => tweets go into 'tweet_queue'
    #tweet_queue = queue.Queue()
    #keywords = ["crypto", "bitcoin", "ethereum", "bonk", "trump"]
    #stream = start_twitter_stream(keywords, tweet_queue)

    # 5) Start tweet consumer in a background thread
    #consumer_thread = threading.Thread(
        #target=tweet_consumer_loop,
        #args=(tweet_queue, sentiment_manager),
        #daemon=True
    #)
    #consumer_thread.start()

    # 6) Start AI trading loop in another background thread
    trader_thread = threading.Thread(
        target=ai_trading_loop,
        args=(model, product_ids, sentiment_manager),
        daemon=True
    )
    trader_thread.start()

    # 7) Start Telegram bot in the main thread
    main_bot()

if __name__ == "__main__":
    main()