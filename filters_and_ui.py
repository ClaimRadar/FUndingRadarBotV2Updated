user_alerts = {}
premium_users = [123456789]  # Örnek kullanıcı ID listesi

def set_user_alert(user_id, symbol, threshold):
    if user_id not in user_alerts:
        user_alerts[user_id] = {}
    user_alerts[user_id][symbol] = threshold

def get_user_alerts(user_id):
    return user_alerts.get(user_id, {})

def is_premium_user(user_id):
    return user_id in premium_users

def get_user_plan_limits(is_premium):
    if is_premium:
        return ("10+ coins", "Binance, Bybit, OKX, MEXC", "%0.1–2.0 custom")
    else:
        return ("1 coin", "1 exchange", "Fixed at %1.0")
