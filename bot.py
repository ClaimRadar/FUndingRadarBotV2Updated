import os
import telebot
from telebot import types
from filters_and_ui import get_user_data, update_user_data, is_premium, get_main_menu
from funding_alerts import get_funding_rate, get_funding_emoji

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# /start handler
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    plan = user_data['plan']
    limits = (
        f"🎯 *Your current limits:*\n"
        f"- Coin tracking: {'1' if plan == 'free' else '10+'}\n"
        f"- Exchanges: {'1 exchange' if plan == 'free' else 'All 4 major exchanges'}\n"
        f"- Alert threshold: {'Fixed at ±1.0%' if plan == 'free' else 'Customizable'}\n"
        f"- Update speed: {'Hourly alerts' if plan == 'free' else 'Real-time alerts'}\n"
    )

    welcome_text = (
        "👋 *Welcome to FundingRadarBot!*\n\n"
        "📡 Get real-time alerts for funding rate changes from:\n"
        "🔹 Binance\n🔹 Bybit\n🔹 OKX\n🔹 MEXC\n\n"
        f"💎 _Plan:_ {plan.capitalize()} (Upgrade to Premium any time)\n\n"
        f"{limits}\n"
        "👇 Choose your setup to begin:"
    )

    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu()
    )

# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data.startswith("mode_"):
        mode = data.split("_")[1]
        update_user_data(user_id, "mode", mode)
        bot.answer_callback_query(call.id, f"Tracking mode set to {mode.upper()} ✅")

    elif data == "choose_exchange":
        markup = types.InlineKeyboardMarkup()
        for exch in ["BINANCE", "BYBIT", "OKX", "MEXC"]:
            markup.add(types.InlineKeyboardButton(exch, callback_data=f"exch_{exch}"))
        bot.send_message(call.message.chat.id, "🏦 Select your exchange:", reply_markup=markup)

    elif data.startswith("exch_"):
        exchange = data.split("_")[1]
        update_user_data(user_id, "exchange", exchange)
        bot.answer_callback_query(call.id, f"Exchange set to {exchange} ✅")

    elif data == "edit_settings":
        bot.send_message(call.message.chat.id, "🛠 Editing coming soon...")

    elif data == "premium_info":
        bot.send_message(call.message.chat.id,
            "💎 *Premium Plan Includes:*\n"
            "- 10+ Coins\n"
            "- All 4 Exchanges\n"
            "- Custom Thresholds\n"
            "- Real-Time Alerts\n"
            "- Countdown Support\n"
            "\n👉 Visit [YourPremiumLink] to upgrade.",
            parse_mode="Markdown")

# Manual funding check
@bot.message_handler(commands=['funding'])
def manual_funding(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    coin_list = user_data['coins'] or ['BTCUSDT']
    exchange = user_data['exchange'] or 'BINANCE'

    for symbol in coin_list:
        rate, countdown = get_funding_rate(exchange, symbol)
        if rate is None:
            bot.send_message(message.chat.id, f"⚠️ Could not fetch funding for {symbol}")
            continue

        emoji = get_funding_emoji(rate)
        hours, remainder = divmod(countdown.seconds, 3600)
        mins = remainder // 60
        response = (
            f"{emoji} *{symbol}* Funding Alert\n"
            f"📉 Rate: `{rate:.2f}%`\n"
            f"🕒 Next Funding: {hours}h {mins}m\n"
            f"🏦 Exchange: {exchange}"
        )
        bot.send_message(message.chat.id, response, parse_mode='Markdown')

print("✅ Bot ready")
