import os
import requests
import yfinance as yf

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

PAIRES = {"EURUSD": "EURUSD=X", "USDJPY": "JPY=X"}
TIMEFRAME = "15m"
PERIODE_RSI = 14
SEUIL_HAUT = 70
SEUIL_BAS = 25


def rsi(close, n=14):
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    perte = (-delta.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100 / (1 + gain / perte)


def zone(v):
    if v >= SEUIL_HAUT:
        return "surachat"
    if v <= SEUIL_BAS:
        return "survente"
    return None


def telegram(msg):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=15,
    )
    print("Telegram :", r.status_code, r.text)


for nom, symbole in PAIRES.items():
    df = yf.download(symbole, period="5d", interval=TIMEFRAME,
                     progress=False, auto_adjust=True)
    close = df["Close"].squeeze().dropna()
    r = rsi(close, PERIODE_RSI)
    # -2 = dernière bougie fermée, -3 = celle d'avant
    actuelle, precedente = r.iloc[-2], r.iloc[-3]
    print(f"{nom} : RSI = {actuelle:.1f}")
    if zone(actuelle) and zone(actuelle) != zone(precedente):
        telegram(f"🚨 {nom} ({TIMEFRAME}) : RSI = {actuelle:.1f} → {zone(actuelle)}")

# --- LIGNE DE TEST : à supprimer quand Telegram fonctionne ---
telegram("✅ Test : le bot fonctionne")
