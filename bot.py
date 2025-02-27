import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Import configuration (ensure your .env now defines SOLANA_RPC_URL and SPARK_MINT_ADDRESS)
from config import BOT_TOKEN, ADMIN_CHAT_ID, SOLANA_RPC_URL, SPARK_MINT_ADDRESS
from trade_manager import CoinbaseClient
from solana.rpc.api import Client as SolanaClient
from solana.publickey import PublicKey

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Global storage for user configurations (for demo only – in production use a DB)
# Each user (keyed by Telegram user id) stores:
#   - "wallet": the user's Solana wallet address
#   - "api_key" and "api_secret": exchange API credentials
user_configs = {}

# ------------------------------------------------------------------------------
# SparkTokenClient using Solana
class SparkTokenClient:
    def __init__(self, rpc_url, mint_address):
        self.client = SolanaClient(rpc_url)
        self.mint_address = mint_address

    def get_balance(self, wallet_address: str) -> float:
        """
        Query the wallet's token balance for the given mint (Spark token).
        Returns the total balance as a float.
        """
        try:
            owner = PublicKey(wallet_address)
            mint = PublicKey(self.mint_address)
            # Get all token accounts for this owner that match the mint address.
            resp = self.client.get_token_accounts_by_owner(owner, {"mint": str(mint)})
            if not resp.get("result") or not resp["result"]["value"]:
                return 0.0
            total = 0.0
            for token_account in resp["result"]["value"]:
                token_account_pubkey = token_account["pubkey"]
                bal_resp = self.client.get_token_account_balance(token_account_pubkey)
                if "result" in bal_resp and "value" in bal_resp["result"]:
                    balance_info = bal_resp["result"]["value"]
                    amount = balance_info.get("uiAmount", 0)
                    total += amount
            return total
        except Exception as e:
            logger.error(f"Error fetching token balance: {e}")
            return 0.0

    def is_balance_sufficient(self, wallet_address: str, minimum: float = 1_000_000) -> bool:
        """Return True if the wallet's balance is at least the minimum required."""
        balance = self.get_balance(wallet_address)
        return balance >= minimum

# Instantiate the trading client and Spark token client
coinbase_client = CoinbaseClient()
spark_token_client = SparkTokenClient(SOLANA_RPC_URL, SPARK_MINT_ADDRESS)
MINIMUM_SPARK_BALANCE = 1_000_000

# ------------------------------------------------------------------------------
# Helper: Check if user has set a wallet and has sufficient Spark tokens.
def check_user_spark_balance(update: Update, context: CallbackContext) -> bool:
    user_id = update.effective_user.id
    config = user_configs.get(user_id, {})
    wallet = config.get("wallet")
    if not wallet:
        update.message.reply_text(
            "You haven't set your wallet address yet. Use /setwallet <your_wallet_address> to set it."
        )
        return False
    if not spark_token_client.is_balance_sufficient(wallet, MINIMUM_SPARK_BALANCE):
        update.message.reply_text(
            "Your Spark token balance is below the required 1,000,000 tokens. "
            "AI trading is paused until you top up your balance."
        )
        return False
    return True

# ------------------------------------------------------------------------------
# Command Handlers

def start(update: Update, context: CallbackContext):
    text = "Welcome to the 10/10 AI Trading Bot v2!\nPlease choose an option below:"
    buttons = [
        [InlineKeyboardButton("Check Balance", callback_data="menu_balance"),
         InlineKeyboardButton("AI Status", callback_data="menu_status")],
        [InlineKeyboardButton("Help", callback_data="menu_help")],
        [InlineKeyboardButton("Manual Buy", callback_data="menu_buy"),
         InlineKeyboardButton("Manual Sell", callback_data="menu_sell")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    if update.message:
        update.message.reply_text(text, reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

def help_command(update: Update, context: CallbackContext):
    commands = (
        "/start - Show the main menu\n"
        "/help - List commands\n"
        "/status - Check AI performance (placeholder)\n"
        "/buy - Force buy (override AI)\n"
        "/sell - Force sell (override AI)\n"
        "/balance - Check Coinbase balances\n"
        "/setwallet - Set your wallet address for Spark token balance check\n"
        "/setapikey - Set your exchange API keys\n"
        "/config - Show your current configuration\n"
    )
    update.message.reply_text(commands)

def status_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    config = user_configs.get(user_id, {})
    wallet = config.get("wallet")
    if wallet and not spark_token_client.is_balance_sufficient(wallet, MINIMUM_SPARK_BALANCE):
        update.message.reply_text(
            "Warning: Your Spark token balance is below the required 1,000,000 tokens. AI trading is paused."
        )
        return
    update.message.reply_text("AI Performance: +15% this month (placeholder)")

def buy_command(update: Update, context: CallbackContext):
    if not check_user_spark_balance(update, context):
        return
    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text("Usage: /buy <product_id> <funds>\nExample: /buy BTC-USD 50")
            return
        product_id = args[0]
        funds = float(args[1])
        result = coinbase_client.place_market_order(product_id, "buy", funds=funds)
        update.message.reply_text(str(result))
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

def sell_command(update: Update, context: CallbackContext):
    if not check_user_spark_balance(update, context):
        return
    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text("Usage: /sell <product_id> <size>\nExample: /sell BTC-USD 0.001")
            return
        product_id = args[0]
        size = float(args[1])
        result = coinbase_client.place_market_order(product_id, "sell", size=size)
        update.message.reply_text(str(result))
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

def balance_command(update: Update, context: CallbackContext):
    balances = coinbase_client.get_account_balances()
    if isinstance(balances, list) and balances and "error" in balances[0]:
        update.message.reply_text(f"Error retrieving balances: {balances[0]['error']}")
        return
    message = "Coinbase Balances:\n"
    for acc in balances:
        currency = acc["currency"]
        bal = float(acc["balance"])
        if bal > 0:
            message += f"{currency}: {bal}\n"
    update.message.reply_text(message)

# --- New commands for configuration ---

def setwallet_command(update: Update, context: CallbackContext):
    """Store the user's Solana wallet address for Spark token balance checking."""
    user_id = update.effective_user.id
    args = context.args
    if not args:
        update.message.reply_text("Usage: /setwallet <your_wallet_address>")
        return
    wallet_address = args[0]
    try:
        # Validate that the address is a valid Solana public key.
        PublicKey(wallet_address)
    except Exception as e:
        update.message.reply_text(f"Invalid wallet address: {e}")
        return
    user_configs.setdefault(user_id, {})["wallet"] = wallet_address
    update.message.reply_text(f"Wallet address set to: {wallet_address}")

def setapikey_command(update: Update, context: CallbackContext):
    """Store the user's exchange API key and secret."""
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /setapikey <api_key> <api_secret>")
        return
    api_key = args[0]
    api_secret = args[1]
    user_configs.setdefault(user_id, {})["api_key"] = api_key
    user_configs[user_id]["api_secret"] = api_secret
    update.message.reply_text("Exchange API credentials set successfully.")

def config_command(update: Update, context: CallbackContext):
    """Display the current configuration for the user."""
    user_id = update.effective_user.id
    config = user_configs.get(user_id, {})
    wallet = config.get("wallet", "Not set")
    api_key = config.get("api_key", "Not set")
    message = f"Your Configuration:\nWallet Address: {wallet}\nExchange API Key: {api_key}\n"
    update.message.reply_text(message)

# ------------------------------------------------------------------------------
# Inline Menu Callback (updated with new command info)
def menu_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    query.answer()
    if data == "menu_balance":
        balances = coinbase_client.get_account_balances()
        if isinstance(balances, list) and balances and "error" in balances[0]:
            query.edit_message_text(f"Error retrieving balances: {balances[0]['error']}")
            return
        msg = "Coinbase Balances:\n"
        for acc in balances:
            currency = acc["currency"]
            bal = float(acc["balance"])
            if bal > 0:
                msg += f"{currency}: {bal}\n"
        query.edit_message_text(msg)
    elif data == "menu_status":
        query.edit_message_text("AI Performance: +15% this month (placeholder)")
    elif data == "menu_help":
        help_text = (
            "Bot commands:\n"
            "/start - Show main menu\n"
            "/help - List commands\n"
            "/status - Check AI performance (placeholder)\n"
            "/buy - Force buy\n"
            "/sell - Force sell\n"
            "/balance - Check Coinbase balances\n"
            "/setwallet - Set your wallet address\n"
            "/setapikey - Set your exchange API keys\n"
            "/config - Show your current configuration\n"
        )
        query.edit_message_text(help_text)
    elif data == "menu_buy":
        text = "Manual Buy: Use /buy <product_id> <funds>, e.g. /buy BTC-USD 50\nOr type /help for more commands."
        query.edit_message_text(text)
    elif data == "menu_sell":
        text = "Manual Sell: Use /sell <product_id> <size>, e.g. /sell BTC-USD 0.001\nOr type /help for more commands."
        query.edit_message_text(text)
    else:
        query.edit_message_text("Unknown option selected. Please type /start to see the menu again.")

# ------------------------------------------------------------------------------
# Main Bot Entry Point
def main_bot():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Regular commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("status", status_command))
    dispatcher.add_handler(CommandHandler("buy", buy_command))
    dispatcher.add_handler(CommandHandler("sell", sell_command))
    dispatcher.add_handler(CommandHandler("balance", balance_command))
    dispatcher.add_handler(CommandHandler("setwallet", setwallet_command))
    dispatcher.add_handler(CommandHandler("setapikey", setapikey_command))
    dispatcher.add_handler(CommandHandler("config", config_command))

    # Callback for inline keyboard
    dispatcher.add_handler(CallbackQueryHandler(menu_callback))

    # Start the bot (consider switching to webhooks for production)
    updater.start_polling()
    logger.info("Telegram Bot with Interactive Menu is running...")
    updater.idle()

if __name__ == "__main__":
    main_bot()
