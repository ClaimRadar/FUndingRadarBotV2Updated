# funding_alerts.py

import requests
from datetime import datetime, timedelta

# 🔹 Binance
def get_binance_funding_rate(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
        response = requests.get(url)
        data = response.json()

        rate = float(data["lastFundingRate"]) * 100
        funding_time = datetime.utcfromtimestamp(int(data["nextFundingTime"]) // 1000)
        countdown = funding_time - datetime.utcnow()

        return rate, countdown
    except Exception as e:
        print(f"[Binance Error] {e}")
        return None, None

# 🟢 Bybit
def get_bybit_funding_rate(symbol):
    try:
        url = f"https://api.bybit.com/v2/public/funding/prev-funding-rate?symbol={symbol}"
        response = requests.get(url)
        data = response.json()

        rate = float(data["result"]["funding_rate"]) * 100

        now = datetime.utcnow()
        next_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        while next_time < now:
            next_time += timedelta(hours=8)
        countdown = next_time - now

        return rate, countdown
    except Exception as e:
        print(f"[Bybit Error] {e}")
        return None, None

# 🟠 OKX
def get_okx_funding_rate(instId):
    try:
        url = f"https://www.okx.com/api/v5/public/funding-rate?instId={instId}"
        response = requests.get(url)
        data = response.json()

        rate = float(data["data"][0]["fundingRate"]) * 100

        now = datetime.utcnow()
        next_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        while next_time < now:
            next_time += timedelta(hours=8)
        countdown = next_time - now

        return rate, countdown
    except Exception as e:
        print(f"[OKX Error] {e}")
        return None, None

# 🔵 MEXC
def get_mexc_funding_rate(symbol):
    try:
        url = f"https://contract.mexc.com/api/v1/private/fundingRate?symbol={symbol}"
        response = requests.get(url)
        data = response.json()

        rate = float(data["data"]["fundingRate"]) * 100

        now = datetime.utcnow()
        next_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        while next_time < now:
            next_time += timedelta(hours=8)
        countdown = next_time - now

        return rate, countdown
    except Exception as e:
        print(f"[MEXC Error] {e}")
        return None, None

# 🔁 Ortak yönlendirici
def get_funding_rate(exchange, symbol):
    exchange = exchange.upper()
    if exchange == "BINANCE":
        return get_binance_funding_rate(symbol)
    elif exchange == "BYBIT":
        return get_bybit_funding_rate(symbol)
    elif exchange == "OKX":
        return get_okx_funding_rate(symbol)
    elif exchange == "MEXC":
        return get_mexc_funding_rate(symbol)
    else:
        return None, None

# 🎨 Emoji: renkli durum ve 🔥 şiddet
def get_funding_emoji(rate):
    if rate is None:
        return "⚪️"
    
    # 🔥 Funding şiddeti
    fire = ""
    abs_rate = abs(rate)
    if abs_rate >= 1.5:
        fire = "🔥🔥🔥"
    elif abs_rate >= 1.0:
        fire = "🔥🔥"
    elif abs_rate >= 0.5:
        fire = "🔥"

    # 🔴 Negatifse kırmızı, 🟢 pozitife yeşil
    color = "🔴" if rate < 0 else "🟢"
    return f"{color}{fire}"
