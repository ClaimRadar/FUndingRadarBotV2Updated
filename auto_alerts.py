import time
import threading
from filters_and_ui import load_db, is_premium, get_user_data
from funding_alerts import get_funding_rate, get_funding_emoji
from bot import bot

def send_funding_alert(user_id, exchange, symbol, rate, countdown, threshold):
    emoji = get_funding_emoji(rate)
    hours, remainder = divmod(countdown.seconds, 3600)
    minutes = remainder // 60

    msg = (
        f"{emoji} *{symbol} Funding Alert!*\n\n"
        f"📊 Exchange: `{exchange}`\n"
        f"💸 Rate: `{rate:.2f}%`\n"
        f"⏳ Next Funding: `{hours}h {minutes}m`\n"
        f"📈 Threshold: `{threshold}%`\n"
    )

    bot.send_message(user_id, msg, parse_mode="Markdown")

def auto_funding_check_loop():
    while True:
        db = load_db()
        print("🔄 Running funding rate check...")

        for user_id_str, user_data in db.items():
            user_id = int(user_id_str)
            plan = user_data.get("plan", "free")
            coins = user_data.get("coins", [])
            exchange = user_data.get("exchange")
            mode = user_data.get("mode", "mixed")
            threshold = user_data.get("threshold", 1.0)

            # Skip users without full config
            if not exchange or not coins:
                continue

            for symbol in coins:
                rate, countdown = get_funding_rate(exchange, symbol)
                if rate is None:
                    continue

                should_alert = False

                if mode == "mixed" and abs(rate) >= threshold:
                    should_alert = True
                elif mode == "positive" and rate >= threshold:
                    should_alert = True
                elif mode == "negative" and rate <= -threshold:
                    should_alert = True

                if should_alert:
                    send_funding_alert(user_id, exchange, symbol, rate, countdown, threshold)

        # Sleep based on plan
        time.sleep(300 if is_premium(user_id) else 3600)

def start_auto_loop():
    t = threading.Thread(target=auto_funding_check_loop)
    t.daemon = True
    t.start()
