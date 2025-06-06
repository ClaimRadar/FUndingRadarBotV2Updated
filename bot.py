import os
import telebot
from telebot import types
from filters_and_ui import set_user_alert, get_user_alerts, is_premium_user, get_user_plan_limits
from funding_alerts import get_funding_rate

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.chat.id
    is_premium = is_premium_user(user_id)
    coin_limit, exchange_limit, threshold_range = get_user_plan_limits(is_premium)

    welcome_text = (
        "👋 *Welcome to FundingRadarBot!*\n\n"
        "📊 *Plan: {}*\n"
        "🔢 *Coin Limit:* {}\n"
        "🏦 *Exchange Access:* {}\n"
        "🎯 *Threshold Control:* {}\n\n"
        "👇 Choose how you'd like to track funding rates:".format(
            "Premium" if is_premium else "Free",
            coin_limit,
            exchange_limit,
            threshold_range
        )
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔴 Only Negative", callback_data="only_negative"),
        types.InlineKeyboardButton("🟢 Only Positive", callback_data="only_positive"),
        types.InlineKeyboardButton("🟡 Mix Mode", callback_data="mix_mode"),
        types.InlineKeyboardButton("📊 General Tracking", callback_data="general_tracking"),
        types.InlineKeyboardButton("💎 Premium Features", callback_data="premium_features")
    )

    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == "only_negative":
        bot.answer_callback_query(call.id, "Tracking only negative rates ✅")
        bot.send_message(call.message.chat.id, "🔴 Now tracking only negative funding rates.")

    elif call.data == "only_positive":
        bot.answer_callback_query(call.id, "Tracking only positive rates ✅")
        bot.send_message(call.message.chat.id, "🟢 Now tracking only positive funding rates.")

    elif call.data == "mix_mode":
        bot.answer_callback_query(call.id, "Mix mode enabled ✅")
        bot.send_message(call.message.chat.id, "🟡 Now tracking both negative & positive rates.")

    elif call.data == "general_tracking":
        bot.answer_callback_query(call.id, "General tracking enabled ✅")
        bot.send_message(call.message.chat.id, "📊 Now tracking general funding rate changes.")

    elif call.data == "premium_features":
        bot.answer_callback_query(call.id, "Premium access 🔐")
        bot.send_message(call.message.chat.id, "💎 Premium features: 10+ coin tracking, custom thresholds, 4 exchanges.\nSubscribe to unlock!")
