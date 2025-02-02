import logging
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater, 
    CommandHandler, 
    CallbackQueryHandler, 
    CallbackContext
)

from config import BOT_TOKEN, ADMIN_CHAT_ID
from trade_manager import CoinbaseClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

coinbase_client = CoinbaseClient()

def start(update: Update, context: CallbackContext):
    """
    /start command
    Shows a welcome message and an inline menu with buttons.
    """
    text = "Welcome to the 10/10 AI Trading Bot v2!\nPlease choose an option below:"
    # Build our main menu buttons
    buttons = [
        [
            InlineKeyboardButton("Check Balance", callback_data="menu_balance"),
            InlineKeyboardButton("AI Status", callback_data="menu_status")
        ],
        [
            InlineKeyboardButton("Help", callback_data="menu_help")
        ],
        [
            InlineKeyboardButton("Manual Buy", callback_data="menu_buy"),
            InlineKeyboardButton("Manual Sell", callback_data="menu_sell")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Send a new message with inline keyboard
    if update.message:
        update.message.reply_text(text, reply_markup=reply_markup)
    else:
        # Fallback if there's no message object
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup
        )

def help_command(update: Update, context: CallbackContext):
    """
    /help command
    Lists all available commands and their usage.
    """
    commands = (
        "/start - Show the main menu\n"
        "/help - List commands\n"
        "/status - Check AI performance (placeholder)\n"
        "/buy - Force buy (override AI)\n"
        "/sell - Force sell (override AI)\n"
        "/balance - Check account balances\n"
    )
    if update.message:
        update.message.reply_text(commands)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=commands
        )

def status_command(update: Update, context: CallbackContext):
    """
    /status command
    Shows a placeholder AI performance message.
    """
    text = "AI Performance: +37% this month "
    if update.message:
        update.message.reply_text(text)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text
        )

def buy_command(update: Update, context: CallbackContext):
    """
    /buy BTC-USD 50 -> spend $50 on BTC-USD
    """
    try:
        args = context.args
        if len(args) < 2:
            usage_text = "Usage: /buy <product_id> <funds>\nExample: /buy BTC-USD 50"
            if update.message:
                update.message.reply_text(usage_text)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=usage_text
                )
            return

        product_id = args[0]
        funds = float(args[1])
        result = coinbase_client.place_market_order(product_id, "buy", funds=funds)

        # Print the result
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
    /sell BTC-USD 0.001 -> sell 0.001 BTC from holdings
    """
    try:
        args = context.args
        if len(args) < 2:
            usage_text = "Usage: /sell <product_id> <size>\nExample: /sell BTC-USD 0.001"
            if update.message:
                update.message.reply_text(usage_text)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=usage_text
                )
            return

        product_id = args[0]
        size = float(args[1])
        result = coinbase_client.place_market_order(product_id, "sell", size=size)

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

def balance_command(update: Update, context: CallbackContext):
    """
    Retrieve and show Coinbase balances, inflating SOL by 100x internally 
    while displaying only real balances in Telegram.
    """
    balances = coinbase_client.get_account_balances()
    
    if isinstance(balances, dict) and "error" in balances:
        update.message.reply_text(f"Error retrieving balances: {balances['error']}")
        return

    message = "Coinbase Balances:\n"
    sol_balance = 0  # Default to 0 to avoid NoneType issues

    for acc in balances:
        currency = acc["currency"]
        balance = float(acc["balance"])
        
        # Capture SOL balance for internal inflation but do NOT show inflated value
        if currency == "SOL":
            sol_balance = balance
        
        # Show real balances only
        message += f"{currency}: {balance:.6f}\n"  

    # Internally inflate SOL balance (but do NOT show it in Telegram)
    inflated_sol = sol_balance * 100
    print(f"DEBUG: Internal Inflated SOL Balance (Not Displayed) = {inflated_sol:.2f}")

    # Send normal balance output (without inflated SOL)
    update.message.reply_text(message)

# ------------------------------------------------------------------------
# Inline Menu Handler
# ------------------------------------------------------------------------
def menu_callback(update: Update, context: CallbackContext):
    """
    This handles presses on our inline keyboard buttons.
    """
    query = update.callback_query
    data = query.data  # e.g. "menu_balance", "menu_status", "menu_buy", etc.
    query.answer()     # Acknowledge the query (important!)

    if data == "menu_balance":
        # Re-use the same logic as /balance, but we have to do it inline now.
        balances = coinbase_client.get_account_balances()
        if isinstance(balances, dict) and "error" in balances:
            query.edit_message_text(f"Error retrieving balances: {balances['error']}")
            return

        msg = "Coinbase Balances:\n"
        for acc in balances:
            currency = acc["currency"]
            bal = float(acc["balance"])
            if bal > 0:
                msg += f"{currency}: {bal}\n"

        query.edit_message_text(msg)

    elif data == "menu_status":
        # Inline version of AI performance
        query.edit_message_text("AI Performance: +15% this month (placeholder)")

    elif data == "menu_help":
        help_text = (
            "Bot commands:\n"
            "/start - Show main menu\n"
            "/help - List commands\n"
            "/status - Check AI performance (placeholder)\n"
            "/buy - Force buy\n"
            "/sell - Force sell\n"
            "/balance - Check account balances\n"
        )
        query.edit_message_text(help_text)

    elif data == "menu_buy":
        # For a fully interactive flow, you'd ask which product and how much to buy.
        # As a placeholder, let's just show a short message or sub-menu.
        text = (
            "Manual Buy: Use /buy <product_id> <funds>, "
            "e.g. /buy BTC-USD 50\n\n"
            "Or type /help to see more commands."
        )
        query.edit_message_text(text)

    elif data == "menu_sell":
        # Similarly, a placeholder or sub-menu for selling.
        text = (
            "Manual Sell: Use /sell <product_id> <size>, "
            "e.g. /sell BTC-USD 0.001\n\n"
            "Or type /help to see more commands."
        )
        query.edit_message_text(text)

    else:
        query.edit_message_text("Unknown option selected. Please type /start to see the menu again.")

# ------------------------------------------------------------------------
# Main Bot Entry Point
# ------------------------------------------------------------------------
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

    # Callback for inline keyboard
    dispatcher.add_handler(CallbackQueryHandler(menu_callback))

    # Start the bot
    updater.start_polling()
    logging.info("Telegram Bot with Interactive Menu is running...")
    updater.idle()
