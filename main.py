from keep_alive import keep_alive
from bot import bot
from funding_alerts import get_funding_rate, get_funding_emoji, get_next_funding_countdown
from filters_and_ui import load_db, is_premium, get_user_data
import threading
import time

def auto_check_funding_loop():
    def run_loop():
        while True:
            db = load_db()
            for user_id, settings in db.items():
                user_id = int(user_id)
                coins = settings.get("coins", [])
                exchange = settings.get("exchange")
                threshold = settings.get("threshold", 1.0)
                plan = settings.get("plan", "free")

                # Skip if not set
                if not exchange or not coins:
                    continue

                for symbol in coins:
                    rate, countdown = get_funding_rate(exchange, symbol)
                    if rate is None:
                        continue

                    mode = settings.get("mode", "mixed")
                    if mode == "positive" and rate <= threshold:
                        continue
                    if mode == "negative" and rate >= -threshold:
                        continue
                    if abs(rate) < threshold:
                        continue

                    emoji = get_funding_emoji(rate)
                    cd = str(countdown).split('.')[0]
                    msg = (
                        f"{emoji} *{symbol} Funding Alert!*\n\n"
                        f"🏦 Exchange: `{exchange}`\n"
                        f"📊 Rate: `{rate:.2f}%`\n"
                        f"⏰ Next Funding In: `{cd}`\n"
                        f"🎯 Threshold: `±{threshold}%`"
                    )

                    try:
                        bot.send_message(user_id, msg, parse_mode="Markdown")
                    except Exception as e:
                        print(f"❌ Error sending to {user_id}: {e}")

            time.sleep(300)  # 5 dakika (premium için ayarlanabilir)

    thread = threading.Thread(target=run_loop)
    thread.daemon = True
    thread.start()

# Botu başlat
keep_alive()
auto_check_funding_loop()
print("✅ FundingRadarBot is online.")
bot.infinity_polling()
