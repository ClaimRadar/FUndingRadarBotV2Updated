# filters_and_ui.py

from telebot import types
import json

DB_FILE = "db.json"

def load_user_data():
    try:
        with open(DB_FILE, "r") as file:
            return json.load(file)
    except:
        return {}

def save_user_data(data):
    with open(DB_FILE, "w") as file:
        json.dump(data, file, indent=2)

def get_user(user_id):
    users = load_user_data()
    return users.get(str(user_id), None)

def set_user(user_id, user_data):
    users = load_user_data()
    users[str(user_id)] = user_data
    save_user_data(users)

def init_user_if_not_exists(user_id):
    if not get_user(user_id):
        set_user(user_id, {
            "plan": "free",
            "exchange": "Binance",
            "coins": ["BTCUSDT"],
            "threshold": 1.0,
            "mode": "mixed"
        })

def is_premium_user(user_id):
    user = get_user(user_id)
    return user and user.get("plan") == "premium"

# 🟦 Menü - Borsa seçimi
def get_exchange_menu(is_premium):
    markup = types.InlineKeyboardMarkup(row_width=2)
    exchanges = ["Binance", "Bybit"]
    if is_premium:
        exchanges.extend(["OKX", "MEXC"])
    for exch in exchanges:
        markup.add(types.InlineKeyboardButton(exch, callback_data=f"exchange_{exch.lower()}"))
    return markup

# 🟨 Menü - Takip Modu seçimi
def get_mode_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔴 Negative", callback_data="mode_negative"),
        types.InlineKeyboardButton("🟢 Positive", callback_data="mode_positive"),
        types.InlineKeyboardButton("🟡 Mixed", callback_data="mode_mixed")
    )
    return markup

# 🟩 Menü - Threshold ayarı (Premium)
def get_threshold_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for val in [0.1, 0.5, 1.0, 1.5, 2.0]:
        markup.add(types.InlineKeyboardButton(f"±{val}%", callback_data=f"threshold_{val}"))
    return markup

# 🔷 Plan Özeti Mesajı
def get_plan_summary(user_id):
    user = get_user(user_id)
    plan = user.get("plan", "free")
    coins = user.get("coins", [])
    exchange = user.get("exchange", "")
    threshold = user.get("threshold", 1.0)
    mode = user.get("mode", "mixed")

    emoji = "💎" if plan == "premium" else "🆓"
    return (
        f"{emoji} *Your Plan:* `{plan.title()}`\n"
        f"📈 *Exchange:* `{exchange}`\n"
        f"🪙 *Coins:* `{', '.join(coins)}`\n"
        f"🎯 *Threshold:* `±{threshold}%`\n"
        f"📊 *Mode:* `{mode}`"
    )
