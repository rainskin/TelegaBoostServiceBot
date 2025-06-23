import requests
import math
from config import COINGECKO_API_KEY
from core.db import admin


def get_actual_usdt_price():
    """
    Получает актуальный курс монеты TON в USD с помощью CoinGecko API.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": "tether",  # ID монеты TON на CoinGecko
        "vs_currencies": "rub",  # Валюта, в которой хотим получить курс
        "x_cg_demo_api_key": COINGECKO_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Вызовет исключение для ошибок HTTP (4xx или 5xx)
        data = response.json()
        usdt_price = data.get("tether", {}).get("rub")

        if usdt_price:
            print(f"Актуальный курс USDT/RUB: ${usdt_price:.4f} RUB")
            return usdt_price
        else:
            print("Не удалось получить курс USD. Проверьте ID монеты или данные API.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при подключении к API: {e}")
        return None
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        return None




