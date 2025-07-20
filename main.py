import time
import requests
import yfinance as yf
import pytz
from datetime import datetime
from statistics import mean

# 🔐 Твои ключи
CMC_API_KEY = "69c96f60-ca43-480a-83a0-63cdb2c43fb3"
TG_TOKEN = "7533119295:AAG_Hnudjc4hF4ZthROX2_smvvSJ1hk3k6o"
TG_CHAT_ID = "5556108366"

# 🔁 Отслеживаемые пары
CRYPTO_PAIRS = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD"]

# 📊 Объём
def get_volume_analysis(data):
    volumes = data['Volume'].tail(10)
    avg_volume = volumes.mean()
    current_volume = volumes.iloc[-1]
    return "📈 Повышенный интерес" if current_volume > avg_volume * 1.2 else "📉 Средний интерес"

# 🕯 Свечи
def get_candle_signal(data):
    last = data.tail(2)
    if last.iloc[-1]['Close'] > last.iloc[-1]['Open'] and last.iloc[-2]['Close'] < last.iloc[-2]['Open']:
        return "Бычий разворот"
    elif last.iloc[-1]['Close'] < last.iloc[-1]['Open'] and last.iloc[-2]['Close'] > last.iloc[-2]['Open']:
        return "Медвежий разворот"
    else:
        return "Сигналов нет"

# 📰 Новости
def get_news_recommendation():
    headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return "📢 Новости стабильные. Можно торговать." if r.status_code == 200 else "⚠️ Новости нестабильны."
    except:
        return "⚠️ Новости недоступны."

# 📡 Генератор сигналов
def get_signal(pair):
    data = yf.download(pair, period="2d", interval="1h", progress=False)
    if data.empty:
        return None

    candle_signal = get_candle_signal(data)
    volume_info = get_volume_analysis(data)
    trend = "Рост" if data['Close'].iloc[-1] > data['Close'].iloc[-5] else "Падение"
    price_now = data['Close'].iloc[-1]

    if candle_signal == "Сигналов нет":
        return None

    confidence = round(abs(data['Close'].pct_change().tail(5).mean()) * 100, 2)
    return {
        "pair": pair,
        "price": price_now,
        "signal": candle_signal,
        "volume": volume_info,
        "trend": trend,
        "confidence": confidence,
        "duration": 15 if trend == "Рост" else 10
    }

# 📬 Отправка в Telegram
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

# 🔁 Главный цикл
def main():
    while True:
        utc_now = datetime.now(pytz.utc)
        if utc_now.weekday() < 5 or utc_now.hour in range(8, 24):
            for pair in CRYPTO_PAIRS:
                result = get_signal(pair)
                if result is not None:
                    message = (
                        f"📊 <b>Сигнал для: {result['pair']}</b>\n"
                        f"💵 Цена: {result['price']:.2f}$\n"
                        f"🕯 Свеча: {result['signal']}\n"
                        f"📉 Объём: {result['volume']}\n"
                        f"📈 Тренд: {result['trend']}\n"
                        f"🎯 Уверенность: {result['confidence']}%\n"
                        f"⏱ Сделка на: {result['duration']} мин.\n"
                        f"📰 Новости: {get_news_recommendation()}"
                    )
                    send_telegram_message(message)
                else:
                    send_telegram_message(f"🔍 Пара {pair}: подходящих сигналов нет.")
        else:
            send_telegram_message("⏰ Неудачное время для торговли. Жди лучшее окно.")

        time.sleep(60)  # Каждую минуту проверка

if __name__ == "__main__":
    main()

