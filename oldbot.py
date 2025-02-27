import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import BOT_TOKEN, ADMIN_CHAT_ID
from trade_manager import CoinbaseClient

logging.basicConfig(level=logging.INFO)
coinbase_client = CoinbaseClient()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to Spark AI, Your Personal AI Trader")

def help_command(update: Update, context: CallbackContext):
    commands = (
        "/start - Welcome message\n"
        "/help - List commands\n"
        "/status - Check AI performance (placeholder)\n"
        "/buy - Force buy (override AI)\n"
        "/sell - Force sell (override AI)\n"
        "/balance - Check account balances\n"
    )
    update.message.reply_text(commands)

def status_command(update: Update, context: CallbackContext):
    # Real implementation could pull from logs or a database of recent performance
    if update.message:
        # If there's a message, reply to it
        update.message.reply_text("AI Performance: +15% this month (placeholder)")
    else:
        # Otherwise, just send a new message (no replying)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="AI Performance: +15% this month (placeholder)"
        )


def buy_command(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 2:
            if update.message:
                update.message.reply_text("Usage: /buy <product_id> <funds>")
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Usage: /buy <product_id> <funds>"
                )
            return

        product_id = args[0]
        funds = float(args[1])
        result = coinbase_client.place_market_order(product_id, "buy", funds=funds)

        if update.message:
            update.message.reply_text(str(result))
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=str(result)
            )

    except Exception as e:
        err_msg = f"Error: {e}"
        if update.message:
            update.message.reply_text(err_msg)
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=err_msg
            )

def sell_command(update: Update, context: CallbackContext):
    """
    /sell BTC-USD 0.001 -> sell 0.001 BTC
    """
    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text("Usage: /sell <product_id> <size>")
            return
        product_id = args[0]
        size = float(args[1])
        result = coinbase_client.place_market_order(product_id, "sell", size=size)
        update.message.reply_text(str(result))
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

def balance_command(update: Update, context: CallbackContext):
    balances = coinbase_client.get_account_balances()
    if isinstance(balances, dict) and "error" in balances:
        update.message.reply_text(f"Error retrieving balances: {balances['error']}")
        return

    message = "Coinbase Balances:\n"
    for acc in balances:
        currency = acc["currency"]
        balance = float(acc["balance"])
        if balance > 0:
            message += f"{currency}: {balance}\n"
    update.message.reply_text(message)

def main_bot():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("status", status_command))
    dispatcher.add_handler(CommandHandler("buy", buy_command))
    dispatcher.add_handler(CommandHandler("sell", sell_command))
    dispatcher.add_handler(CommandHandler("balance", balance_command))

    updater.start_polling()
    logging.info("Telegram Bot is running...")
    updater.idle()
