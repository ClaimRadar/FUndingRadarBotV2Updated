import os
import telebot
from telebot import types
from filters_and_ui import set_user_alert, get_user_alerts, is_premium_user, get_user_plan_limits
from funding_alerts import get_funding_rate

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_settings = {}

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.chat.id
    is_premium = is_premium_user(user_id)
    coin_limit, exchange_limit, threshold_range = get_user_plan_limits(is_premium)

    welcome_text = (
        "👋 *Welcome to FundingRadarBot!*\n\n"
        "📡 Get real-time alerts for funding rate changes from:\n"
        "🔹 Binance\n🔹 Bybit\n🔹 OKX\n🔹 MEXC\n\n"
        "💎 _Plan:_ {}\n\n"
        "🎯 *Your current limits:*\n"
        "- Coin tracking: {}\n"
        "- Exchanges: {}\n"
        "- Alert threshold: {}\n"
        "- Update speed: {}\n\n"
        "👇 Choose an exchange to begin:"
    ).format(
        "Premium" if is_premium else "Free",
        coin_limit,
        exchange_limit,
        threshold_range,
        "Real-time" if is_premium else "Hourly only"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔹 Binance", callback_data="ex_binance"),
        types.InlineKeyboardButton("🟢 Bybit", callback_data="ex_bybit"),
        types.InlineKeyboardButton("🟠 OKX", callback_data="ex_okx"),
        types.InlineKeyboardButton("🔵 MEXC", callback_data="ex_mexc")
    )
    bot.send_message(user_id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.message.chat.id
    is_premium = is_premium_user(user_id)

    if call.data.startswith("ex_"):
        selected_exchange = call.data.split("_")[1].upper()

        if selected_exchange in ["OKX", "MEXC"] and not is_premium:
            bot.answer_callback_query(call.id, "Premium only 🚫")
            bot.send_message(user_id, "⚠️ Access to {} is only available for Premium users. Upgrade to continue.".format(selected_exchange))
            return

        user_settings[user_id] = {"exchange": selected_exchange}
        bot.answer_callback_query(call.id, f"Exchange set: {selected_exchange}")

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔴 Only Negative", callback_data="mode_negative"),
            types.InlineKeyboardButton("🟢 Only Positive", callback_data="mode_positive"),
            types.InlineKeyboardButton("🟡 Mix Mode", callback_data="mode_mix"),
            types.InlineKeyboardButton("📊 General", callback_data="mode_general")
        )
        bot.send_message(user_id, "✅ Exchange selected: *{}*\n\nNow select your funding alert mode:".format(selected_exchange), parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith("mode_"):
        selected_mode = call.data.split("_")[1]
        user_settings[user_id]["mode"] = selected_mode
        bot.answer_callback_query(call.id, f"Tracking mode set: {selected_mode}")
        bot.send_message(user_id, f"🛠 Settings saved!\n\n🔁 You will now receive alerts for *{user_settings[user_id]['exchange']}* using *{selected_mode}* mode.", parse_mode="Markdown")

    elif call.data == "premium_features":
        bot.answer_callback_query(call.id, "Premium access 🔐")
        bot.send_message(call.message.chat.id, "💎 Premium features include:\n- 10+ coin tracking\n- All 4 exchanges\n- Custom alerts\n- Countdown & daily summaries\n\nSubscribe for $7/month or $15/3 months.")
