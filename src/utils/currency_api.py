import requests
import math
from config import COINGECKO_API_KEY


def get_usdt_price():
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
            print("Не удалось получить курс TON. Проверьте ID монеты или данные API.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при подключении к API: {e}")
        return None
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        return None


# наценка к курсу USDT/RUB - 5%
# Найти курс рубля к XTR

get_usdt_price()

# --- КОНСТАНТЫ (могут быть вынесены в конфиг или БД) ---
TELEGRAM_STAR_TO_USD_EQUIVALENT = 0.013  # USD за 1 Star (по данным Telegram)
TON_TO_USDT_SPOT_FEE_PERCENT = 0.001  # 0.1% комиссия Binance за спотовую торговлю TON/USDT
TON_NETWORK_FEE_PERCENT = 0.0005  # Условная комиссия за газ TON (0.05%, может быть скорректирована)

# Этот процент будет храниться в твоей БД и редактироваться вручную.
# Например, 0.02 означает, что P2P курс будет на 2% выше официального USD/RUB.
P2P_PREMIUM_PERCENT_FROM_DB = 0.05  # <-- Пример: 5% наценка для P2P


# --- ГЛАВНАЯ ФУНКЦИЯ РАСЧЕТА ЦЕНЫ ---
def calculate_stars_price(service_price_rub):
    """
    Рассчитывает цену услуги в Telegram Stars, учитывая базовый курс USD/RUB из API
    и P2P-наценку, а также все комиссии.

    Args:
        service_price_rub (float): Исходная цена услуги в рублях (уже с маржой).

    Returns:
        int: Количество Telegram Stars, округленное в большую сторону, или None в случае ошибки.
    """
    if service_price_rub <= 0:
        print("Ошибка: Цена услуги в рублях должна быть положительной.")
        return None

    # 1. Получаем актуальный базовый курс USDT/RUB
    usd_to_rub_rate = get_usdt_price()
    if usd_to_rub_rate is None:
        print("Не удалось получить базовый курс USD/RUB. Расчет невозможен.")
        return None

    # 2. Рассчитываем P2P_USDT_TO_RUB_RATE
    # P2P_PREMIUM_PERCENT_FROM_DB берется из твоей БД.
    if P2P_PREMIUM_PERCENT_FROM_DB < 0:
        print("Ошибка: Процент P2P-наценки не может быть отрицательным.")
        return None

    p2p_usdt_to_rub_rate = usd_to_rub_rate * (1 + P2P_PREMIUM_PERCENT_FROM_DB)
    print(
        f"Рассчитанный P2P USDT/RUB курс "
        f"(с наценкой {P2P_PREMIUM_PERCENT_FROM_DB * 100:.2f}%): 1 USDT ≈ {p2p_usdt_to_rub_rate:.4f} RUB")

    # 3. Сколько USDT нужно получить чистыми на P2P
    try:
        required_usdt_net = service_price_rub / p2p_usdt_to_rub_rate
    except ZeroDivisionError:
        print("Ошибка: Рассчитанный P2P_USDT_TO_RUB_RATE оказался нулевым.")
        return None

    # 4. Сколько USD нужно, чтобы хватило после всех комиссий (спот + газ TON)
    if TON_TO_USDT_SPOT_FEE_PERCENT >= 1.0 or TON_TO_USDT_SPOT_FEE_PERCENT < 0:
        print("Ошибка: Процент спотовой комиссии должен быть между 0 и 1.")
        return None
    usd_after_ton_spot_fee = required_usdt_net / (1 - TON_TO_USDT_SPOT_FEE_PERCENT)

    if TON_NETWORK_FEE_PERCENT >= 1.0 or TON_NETWORK_FEE_PERCENT < 0:
        print("Ошибка: Процент сетевой комиссии TON должен быть между 0 и 1.")
        return None
    usd_total_required = usd_after_ton_spot_fee / (1 - TON_NETWORK_FEE_PERCENT)

    # 5. Сколько Stars требуется
    stars_raw = usd_total_required / TELEGRAM_STAR_TO_USD_EQUIVALENT

    # Округляем в большую сторону до целого числа Stars
    num_stars = math.ceil(stars_raw)

    print(f"\n--- Детализация расчета ---")
    print(f"Исходная цена услуги (RUB): {service_price_rub:.2f} RUB")
    print(f"Необходимая чистая сумма USDT (для получения {service_price_rub} RUB): {required_usdt_net:.4f} USDT")
    print(f"USDT с учетом комиссии спота TON/USDT: {usd_after_ton_spot_fee:.4f} USD")
    print(f"через USDT с учетом комиссии за газ TON: {usd_total_required:.4f} USD")
    print(f"Необходимое количество Stars (до округления): {stars_raw:.2f}")
    print(f"\nИтоговая цена в Telegram Stars: {num_stars} Stars")

    return int(num_stars)


# Пример использования:
price_in_rub = 1500.0  # Твоя цена услуги в рублях, уже с маржой

calculated_stars = calculate_stars_price(price_in_rub)

if calculated_stars is not None:
    print(f"\nДля услуги стоимостью {price_in_rub} RUB, рекомендуемая цена: {calculated_stars} Telegram Stars.")
