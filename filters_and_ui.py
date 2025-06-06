# filters_and_ui.py

# 🔐 Premium kullanıcı listesi (Telegram user_id)
premium_users = [1055454475]  # Kendi ID’ni buraya yaz

# 🧠 Kullanıcıların ayarladığı özel coin + threshold bilgileri
user_alerts = {}

# 🚀 Alert ayarı kaydet
def set_user_alert(user_id, symbol, threshold):
    if user_id not in user_alerts:
        user_alerts[user_id] = {}
    user_alerts[user_id][symbol] = threshold

# 🧾 Alert bilgisi getir
def get_user_alerts(user_id):
    return user_alerts.get(user_id, {})

# 💎 Premium kullanıcı kontrolü
def is_premium_user(user_id):
    return user_id in premium_users

# 🧮 Kullanıcının planına göre limit bilgisi
def get_user_plan_limits(is_premium):
    if is_premium:
        return (
            "10+ coins",
            "Binance, Bybit, OKX, MEXC",
            "%0.1–2.0 custom"
        )
    else:
        return (
            "1 coin",
            "1 exchange",
            "Fixed at ±1.0"
        )
