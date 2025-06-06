import os
import telebot
from telebot import types
from filters_and_ui import set_user_alert, get_user_alerts, is_premium_user, get_user_plan_limits
from funding_alerts import get_funding_rate

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_settings = {}
ADMIN_ID = 123456789  # kendi Telegram user ID'n ile değiştir

# /start komutu – Hoş geldin + plan bilgisi + ilk seçim
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

# Menü tıklamaları
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.message.chat.id
    is_premium = is_premium_user(user_id)

    if call.data.startswith("mode_"):
        selected_mode = call.data.split("_")[1]
        user_settings[user_id] = {"mode": selected_mode}
        bot.answer_callback_query(call.id, f"Tracking mode set: {selected_mode}")
        bot.send_message(
            user_id,
            f"🛠 Settings saved!\n\n🔁 You will now receive alerts using *{selected_mode}* mode.",
            parse_mode="Markdown"
        )

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

# /status komutu – Bot aktif mi?
@bot.message_handler(commands=["status"])
def status_handler(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "ℹ️ Bot is online.")
    else:
        bot.send_message(message.chat.id,
                         "✅ *FundingRadarBot is online and running!*\n\n🕒 Status: `ACTIVE`\n📈 Funding data is being tracked.\n\nNeed help? Type /help or /start.",
                         parse_mode="Markdown")

# /help komutu – Komut listesi
@bot.message_handler(commands=["help"])
def help_handler(message):
    help_text = (
        "🆘 *FundingRadarBot Commands:*\n\n"
        "/start – Start the bot and choose your settings\n"
        "/status – Check if the bot is running\n"
        "/help – Show this help message\n"
        "/edit – (coming soon) Modify your alert settings\n"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")
