# config.py

import os
from dotenv import load_dotenv

load_dotenv()  # This will read in the .env file

# =============================
# TELEGRAM
# =============================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "YOUR_TELEGRAM_CHAT_ID")

# =============================
# COINBASE ADVANCED TRADE
# =============================
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY", "organizations/{org_id}/apiKeys/{key_id}")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET", """-----BEGIN EC PRIVATE KEY-----
...
-----END EC PRIVATE KEY-----
""")

# =============================
# ML / RL CONFIG
# =============================
RL_ALGO = "PPO"
TRAIN_TIMESTEPS = 200000
MODEL_SAVE_PATH = "models/ppo_trader_v2"

# =============================
# RISK MANAGEMENT
# =============================
MAX_POSITION_PERCENT = 0.2
MAX_DRAWDOWN_PERCENT = 0.3
TRANSACTION_FEE_PERCENT = 0.001

# =============================
# SENTIMENT 
# =============================
SENTIMENT_THRESHOLD = 0.65

# =============================
# TWITTER / X
# =============================
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
