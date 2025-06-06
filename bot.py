# bot.py
import os
import telebot
from telebot import types
from filters_and_ui import *
from funding_alerts import fetch_all_funding_data, format_funding_message
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ✦✦ START COMMAND ✦✦
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    init_user_if_not_exists(user_id)
    is_premium = is_premium_user(user_id)

    welcome_text = (
        "👋 *Welcome to FundingRadarBot!*\n\n"
        "📡 Real-time alerts from: Binance, Bybit, OKX, MEXC\n"
        f"{get_plan_summary(user_id)}\n\n"
        "📌 Choose a setting to edit below:"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🌐 Exchange", callback_data="menu_exchange"),
        types.InlineKeyboardButton("📊 Mode", callback_data="menu_mode"),
    )
    if is_premium:
        markup.add(types.InlineKeyboardButton("🎯 Threshold", callback_data="menu_threshold"))
    markup.add(types.InlineKeyboardButton("🔄 Check Funding Now", callback_data="fetch_funding"))

    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# ✦✦ CALLBACK HANDLERS ✦✦
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    data = call.data

    if data.startswith("menu_exchange"):
        bot.send_message(call.message.chat.id, "Select an exchange:", reply_markup=get_exchange_menu(is_premium_user(user_id)))

    elif data.startswith("menu_mode"):
        bot.send_message(call.message.chat.id, "Choose alert mode:", reply_markup=get_mode_menu())

    elif data.startswith("menu_threshold"):
        bot.send_message(call.message.chat.id, "Set your threshold:", reply_markup=get_threshold_menu())

    elif data.startswith("exchange_"):
        exch = data.split("_")[1].capitalize()
        user = get_user(user_id)
        user["exchange"] = exch
        set_user(user_id, user)
        bot.answer_callback_query(call.id, f"Exchange set to {exch}!")

    elif data.startswith("mode_"):
        mode = data.split("_")[1]
        user = get_user(user_id)
        user["mode"] = mode
        set_user(user_id, user)
        bot.answer_callback_query(call.id, f"Mode set to {mode}!")

    elif data.startswith("threshold_"):
        val = float(data.split("_")[1])
        user = get_user(user_id)
        user["threshold"] = val
        set_user(user_id, user)
        bot.answer_callback_query(call.id, f"Threshold set to ±{val}%!")

    elif data == "fetch_funding":
        user = get_user(user_id)
        msg = format_funding_message(user)
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

# ▶️ POLLING
print("🤖 Bot is running...")
bot.infinity_polling()
