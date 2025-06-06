import requests
from datetime import datetime, timedelta

# 🔥 Emoji formatting

def format_rate_emoji(rate):
    if rate >= 1.5 or rate <= -1.5:
        fire = "🔥🔥🔥"
    elif rate >= 1 or rate <= -1:
        fire = "🔥🔥"
    elif rate >= 0.5 or rate <= -0.5:
        fire = "🔥"
    else:
        fire = ""

    color = "🟢" if rate > 0 else "🔴" if rate < 0 else "🟡"
    return f"{color}{fire}"

# ⏳ Funding countdown

def get_funding_countdown():
    now = datetime.utcnow()
    next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=8))
    remaining = next_hour - now
    return f"{remaining.seconds // 3600}h {(remaining.seconds % 3600) // 60}m"

# 📡 Funding rate fetchers

def get_binance_rate(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
        res = requests.get(url)
        rate = float(res.json()["lastFundingRate"]) * 100
        return rate
    except:
        return None

def get_bybit_rate(symbol):
    try:
        url = f"https://api.bybit.com/v2/public/funding/prev-funding-rate?symbol={symbol}"
        res = requests.get(url)
        rate = float(res.json()["result"]["funding_rate"]) * 100
        return rate
    except:
        return None

def get_okx_rate(symbol):
    try:
        url = f"https://www.okx.com/api/v5/public/funding-rate?instId={symbol}"
        res = requests.get(url)
        rate = float(res.json()["data"][0]["fundingRate"]) * 100
        return rate
    except:
        return None

def get_mexc_rate(symbol):
    try:
        url = f"https://www.mexc.com/open/api/v2/market/funding_rate?symbol={symbol}"
        res = requests.get(url)
        rate = float(res.json()["data"]["funding_rate"]) * 100
        return rate
    except:
        return None
