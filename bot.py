import os
import telebot
from telebot import types
from filters_and_ui import get_main_menu, get_user_data, update_user_data, is_premium
from funding_alerts import get_funding_rate, get_funding_emoji, get_next_funding_countdown

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# 🔹 /start komutu
@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    plan = user_data.get("plan", "free")

    welcome_text = (
        f"👋 *Welcome to FundingRadarBot!*\n\n"
        f"📡 Get real-time alerts for funding rate changes from:\n"
        f"🔹 Binance\n🔹 Bybit\n🔹 OKX\n🔹 MEXC\n\n"
        f"💎 _Plan:_ {plan.capitalize()} (Use /upgrade to change)\n\n"
        f"🎯 *Your current limits:*\n"
        f"- Coin tracking: {'10+' if plan == 'premium' else '1 coin'}\n"
        f"- Exchanges: {'All major exchanges' if plan == 'premium' else '1 exchange'}\n"
        f"- Alert threshold: {'Custom' if plan == 'premium' else 'Fixed at ±1.0%'}\n"
        f"- Update speed: {'Real-time alerts' if plan == 'premium' else 'Hourly only'}\n\n"
        f"👇 Choose your tracking setup:"
    )

    bot.send_message(user_id, welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())

# 🔹 Funding Mode Değişimi
@bot.callback_query_handler(func=lambda call: call.data.startswith("mode_"))
def mode_select_handler(call):
    mode = call.data.replace("mode_", "")
    update_user_data(call.from_user.id, "mode", mode)
    bot.answer_callback_query(call.id, f"Tracking mode set to: {mode}")
    bot.send_message(call.message.chat.id, f"📡 Mode updated to `{mode}`", parse_mode="Markdown")

# 🔹 Plan Bilgisi Gösterme
@bot.callback_query_handler(func=lambda call: call.data == "premium_info")
def premium_info_handler(call):
    bot.send_message(call.message.chat.id,
        "💎 *Upgrade to Premium*\n\n"
        "✅ Track 10+ coins\n"
        "✅ All 4 exchanges\n"
        "✅ Custom thresholds\n"
        "✅ Real-time alerts\n"
        "✅ Countdown summaries\n\n"
        "👉 DM @FundingRadar for access",
        parse_mode="Markdown")

# 🔹 /edit komutu
@bot.message_handler(commands=["edit"])
def edit_handler(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    msg = (
        f"🛠 *Edit Your Settings*\n\n"
        f"💎 Plan: `{user_data.get('plan')}`\n"
        f"🏦 Exchange: `{user_data.get('exchange') or 'Not set'}`\n"
        f"💰 Coins: `{', '.join(user_data.get('coins') or []) or 'None'}`\n"
        f"📈 Threshold: `{user_data.get('threshold')}%`\n"
        f"📡 Mode: `{user_data.get('mode')}`\n\n"
        f"Choose what you want to change:"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🏦 Exchange", callback_data="edit_exchange"),
        types.InlineKeyboardButton("💰 Coins", callback_data="edit_coins"),
        types.InlineKeyboardButton("📈 Threshold", callback_data="edit_threshold"),
        types.InlineKeyboardButton("📡 Mode", callback_data="edit_mode")
    )

    bot.send_message(user_id, msg, parse_mode="Markdown", reply_markup=markup)

# 🔹 Callback: edit menüsü
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def edit_callback_handler(call):
    user_id = call.from_user.id

    if call.data == "edit_exchange":
        bot.send_message(user_id, "🏦 Enter new exchange (Binance / Bybit / OKX / MEXC):")
        bot.register_next_step_handler(call.message, process_exchange_edit)

    elif call.data == "edit_coins":
        bot.send_message(user_id, "💰 Enter coins to track (comma separated, e.g., BTCUSDT,ETHUSDT):")
        bot.register_next_step_handler(call.message, process_coins_edit)

    elif call.data == "edit_threshold":
        bot.send_message(user_id, "📈 Enter your custom threshold (e.g. 0.5):")
        bot.register_next_step_handler(call.message, process_threshold_edit)

    elif call.data == "edit_mode":
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("🔴 Negative", callback_data="set_mode_negative"),
            types.InlineKeyboardButton("🟢 Positive", callback_data="set_mode_positive"),
            types.InlineKeyboardButton("🌀 Mixed", callback_data="set_mode_mixed")
        )
        bot.send_message(user_id, "📡 Select funding rate tracking mode:", reply_markup=markup)

# 🔹 Mod ayarı sonrası
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_mode_"))
def set_mode_handler(call):
    mode = call.data.replace("set_mode_", "")
    update_user_data(call.from_user.id, "mode", mode)
    bot.answer_callback_query(call.id, f"✅ Mode set to {mode}")
    bot.send_message(call.message.chat.id, f"Funding rate mode updated to `{mode}`", parse_mode="Markdown")

# 🔹 Ayar işleme fonksiyonları
def process_exchange_edit(message):
    exchange = message.text.strip().upper()
    if exchange in ["BINANCE", "BYBIT", "OKX", "MEXC"]:
        update_user_data(message.from_user.id, "exchange", exchange)
        bot.send_message(message.chat.id, f"✅ Exchange updated to {exchange}.")
    else:
        bot.send_message(message.chat.id, "❌ Invalid exchange. Choose: Binance, Bybit, OKX, MEXC.")

def process_coins_edit(message):
    coins = [x.strip().upper() for x in message.text.split(",")]
    plan = get_user_data(message.from_user.id).get("plan")
    if plan == "free" and len(coins) > 1:
        bot.send_message(message.chat.id, "❌ Free plan allows only 1 coin. Upgrade to Premium.")
    else:
        update_user_data(message.from_user.id, "coins", coins)
        bot.send_message(message.chat.id, f"✅ Coins updated to: {', '.join(coins)}")

def process_threshold_edit(message):
    try:
        val = float(message.text)
        if 0.1 <= val <= 5.0:
            update_user_data(message.from_user.id, "threshold", val)
            bot.send_message(message.chat.id, f"✅ Threshold set to ±{val}%")
        else:
            bot.send_message(message.chat.id, "❌ Enter a number between 0.1 and 5.0")
    except:
        bot.send_message(message.chat.id, "❌ Invalid input. Please enter a number.")

# 🔹 /upgrade komutu
@bot.message_handler(commands=["upgrade"])
def upgrade_handler(message):
    bot.send_message(message.chat.id,
        "💎 *Upgrade to Premium*\n\n"
        "✅ Track 10+ coins\n"
        "✅ All 4 exchanges\n"
        "✅ Custom thresholds\n"
        "✅ Real-time alerts\n"
        "✅ Countdown summaries\n\n"
        "👉 DM @FundingRadar for access",
        parse_mode="Markdown")

# ▶️ Botu başlat
print("🤖 Bot is running...")
bot.infinity_polling()
