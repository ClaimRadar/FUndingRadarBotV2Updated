# funding_alerts.py

import requests

# 🔹 Binance Funding Rate
def get_binance_funding_rate(symbol):
    url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return float(data["lastFundingRate"]) * 100  # % cinsinden

# 🟢 Bybit Funding Rate
def get_bybit_funding_rate(symbol):
    url = f"https://api.bybit.com/v2/public/funding/prev-funding-rate?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return float(data["result"]["funding_rate"]) * 100

# 🟠 OKX Funding Rate
def get_okx_funding_rate(instId):
    url = f"https://www.okx.com/api/v5/public/funding-rate?instId={instId}"
    response = requests.get(url)
    data = response.json()
    return float(data["data"][0]["fundingRate"]) * 100

# 🔵 MEXC Funding Rate
def get_mexc_funding_rate(symbol):
    url = f"https://contract.mexc.com/api/v1/private/fundingRate?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return float(data["data"]["fundingRate"]) * 100

# 🔀 Ortak arayüz – borsa adına göre yönlendir
def get_funding_rate(exchange, symbol):
    try:
        if exchange == "BINANCE":
            return get_binance_funding_rate(symbol)
        elif exchange == "BYBIT":
            return get_bybit_funding_rate(symbol)
        elif exchange == "OKX":
            return get_okx_funding_rate(symbol)
        elif exchange == "MEXC":
            return get_mexc_funding_rate(symbol)
        else:
            return None
    except Exception as e:
        print(f"[ERROR] Funding rate fetch failed for {exchange} {symbol} – {e}")
        return None
