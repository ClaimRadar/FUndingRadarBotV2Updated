import os
import telebot
from telebot import types
from filters_and_ui import is_premium_user
from funding_alerts import get_funding_rate

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_settings = {}
ADMIN_ID = 123456789  # Kendi Telegram ID'n ile değiştir

# /start – Hoş geldin mesajı ve plan bilgisi
@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.chat.id
    is_premium = is_premium_user(user_id)

    if is_premium:
        plan_block = (
            "💎 _Plan:_ Premium\n\n"
            "🎯 *Your current limits:*\n"
            "- Coin tracking: 10+ coins\n"
            "- Exchanges: All 4 (Binance, Bybit, OKX, MEXC)\n"
            "- Alert threshold: Custom (0.1–2.0%)\n"
            "- Update speed: Real-time alerts\n\n"
            "✅ You have access to all premium features.\n"
        )
    else:
        plan_block = (
            "💎 _Plan:_ Free (Upgrade to Premium any time)\n\n"
            "🎯 *Your current limits:*\n"
            "- Coin tracking: 1 coin\n"
            "- Exchanges: 1 exchange\n"
            "- Alert threshold: Fixed at ±1.0%\n"
            "- Update speed: Hourly alerts only\n\n"
            "Upgrade to Premium for:\n"
            "✅ 10+ coins\n"
            "✅ All 4 major exchanges\n"
            "✅ Custom alerts\n"
            "✅ Countdown & daily summaries\n"
        )

    welcome_text = (
        "👋 *Welcome to FundingRadarBot!*\n\n"
        "📡 Get real-time alerts for funding rate changes from:\n"
        "🔹 Binance\n"
        "🔹 Bybit\n"
        "🔹 OKX\n"
        "🔹 MEXC\n\n"
        + plan_block +
        "\n👇 Choose how you'd like to track funding rates:"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔴 Only Negative", callback_data="mode_negative"),
        types.InlineKeyboardButton("🟢 Only Positive", callback_data="mode_positive"),
        types.InlineKeyboardButton("🟡 Mix Mode", callback_data="mode_mix"),
        types.InlineKeyboardButton("📊 General Tracking", callback_data="mode_general"),
        types.InlineKeyboardButton("💎 Premium Features", callback_data="premium_features")
    )

    bot.send_message(user_id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# /edit – Borsa ve takip modunu değiştir
@bot.message_handler(commands=["edit"])
def edit_handler(message):
    user_id = message.chat.id
    is_premium = is_premium_user(user_id)

    bot.send_message(
        user_id,
        "🛠 *Edit your settings below:*\n\nChoose your exchange to continue.",
        parse_mode="Markdown"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔹 Binance", callback_data="edit_ex_binance"),
        types.InlineKeyboardButton("🟢 Bybit", callback_data="edit_ex_bybit"),
        types.InlineKeyboardButton("🟠 OKX", callback_data="edit_ex_okx"),
        types.InlineKeyboardButton("🔵 MEXC", callback_data="edit_ex_mexc")
    )
    bot.send_message(user_id, "📊 Select a new exchange:", reply_markup=markup)

# /status – Bot çalışıyor mu kontrol
@bot.message_handler(commands=["status"])
def status_handler(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "ℹ️ Bot is online.")
    else:
        bot.send_message(message.chat.id,
                         "✅ *FundingRadarBot is online and running!*\n\n🕒 Status: `ACTIVE`\n📈 Funding data is being tracked.\n\nNeed help? Type /help or /start.",
                         parse_mode="Markdown")

# /help – Yardım komutları
@bot.message_handler(commands=["help"])
def help_handler(message):
    help_text = (
        "🆘 *FundingRadarBot Commands:*\n\n"
        "/start – Start the bot and choose your settings\n"
        "/edit – Update your exchange or tracking mode\n"
        "/status – Check if the bot is running\n"
        "/help – Show this help message\n"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# Inline buton callback yönetimi
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.message.chat.id
    is_premium = is_premium_user(user_id)

    # Başlangıç ekranı tracking mode seçimi
    if call.data.startswith("mode_"):
        selected_mode = call.data.split("_")[1]
        user_settings[user_id] = {"mode": selected_mode}
        bot.answer_callback_query(call.id, f"Tracking mode set: {selected_mode}")
        bot.send_message(
            user_id,
            f"🛠 Settings saved!\n\n🔁 You will now receive alerts using *{selected_mode}* mode.",
            parse_mode="Markdown"
        )

    # Premium özellik bilgilendirme
    elif call.data == "premium_features":
        bot.answer_callback_query(call.id, "Premium access 🔐")
        bot.send_message(
            user_id,
            "💎 Premium features include:\n"
            "- 10+ coin tracking\n"
            "- All 4 exchanges\n"
            "- Custom alerts\n"
            "- Countdown & daily summaries\n\n"
            "Subscribe for $7/month or $15/3 months."
        )

    # Edit ekranı – borsa seçimi
    elif call.data.startswith("edit_ex_"):
        selected_exchange = call.data.split("_")[2].upper()

        if selected_exchange in ["OKX", "MEXC"] and not is_premium:
            bot.send_message(user_id, f"🚫 {selected_exchange} is Premium only. Upgrade to use this exchange.")
            return

        if user_id not in user_settings:
            user_settings[user_id] = {}
        user_settings[user_id]["exchange"] = selected_exchange

        bot.send_message(
            user_id,
            f"✅ Exchange updated to *{selected_exchange}*.\nNow select a new funding alert mode:",
            parse_mode="Markdown"
        )

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔴 Only Negative", callback_data="edit_mode_negative"),
            types.InlineKeyboardButton("🟢 Only Positive", callback_data="edit_mode_positive"),
            types.InlineKeyboardButton("🟡 Mix Mode", callback_data="edit_mode_mix"),
            types.InlineKeyboardButton("📊 General", callback_data="edit_mode_general")
        )
        bot.send_message(user_id, "🎯 Select alert mode:", reply_markup=markup)

    # Edit ekranı – funding mode değişimi
    elif call.data.startswith("edit_mode_"):
        selected_mode = call.data.split("_")[2]
        if user_id not in user_settings:
            user_settings[user_id] = {}
        user_settings[user_id]["mode"] = selected_mode

        bot.send_message(
            user_id,
            f"🔁 Your alert mode has been updated to *{selected_mode}*.\nSettings saved ✅",
            parse_mode="Markdown"
        )

# Başlat
print("🤖 FundingRadarBot is running...")
bot.infinity_polling()
