import math

from core.db import admin
from utils.currencies import usdt


def convert_to_stars(service_price_rub):
    """
   Calculates the price of the service in Telegram Stars, taking into account the basic USD/RUB course from the API
    and P2P invoice, as well as all commissions.

    Args:
        service_price_rub (Float): The initial price of the service in rubles (already with margin).

    Returns:
        Int: The number of Telegram Stars, rounded up, or None in case of error.
    """

    commissions = admin.get_recharge_xtr_commissions()
    telegram_star_to_usd_equivalent = commissions.get('telegram_star_to_usd_equivalent')  # TODO: избавиться от п2п курса и, возможно, других комиссий. Сейчас в БД значение п2п комсы = 0
    ton_to_usdt_spot_fee_percent = commissions.get('ton_to_usdt_spot_fee_percent')
    ton_network_fee_percent = commissions.get('ton_network_fee_percent')
    p2p_premium_percent = commissions.get('p2p_premium_percent_from_db')

    if service_price_rub <= 0:
        print("Error: The price of the service in rubles should be positive.")
        return None

    # 1. Получаем актуальный базовый курс USDT/RUB
    usd_to_rub_rate = usdt.to_rub_rate()
    if usd_to_rub_rate is None:
        print("It was not possible to get the base course of the USD/RUB. The calculation is impossible.")
        return None

    # 2. Рассчитываем P2P_USDT_TO_RUB_RATE
    if p2p_premium_percent < 0:
        print("Error: The percentage of the P2P invoice cannot be negative.")
        return None

    p2p_usdt_to_rub_rate = usd_to_rub_rate * (1 + p2p_premium_percent)
    print(
        f"Рассчитанный P2P USDT/RUB курс "
        f"(с наценкой {p2p_premium_percent * 100:.2f}%): 1 USDT ≈ {p2p_usdt_to_rub_rate:.4f} RUB")

    # 3. How many USDT need to get clean on p2p
    try:
        required_usdt_net = service_price_rub / p2p_usdt_to_rub_rate
    except ZeroDivisionError:
        print("Ошибка: Рассчитанный P2P_USDT_TO_RUB_RATE оказался нулевым.")
        return None

    # 4. Сколько USD нужно, чтобы хватило после всех комиссий (спот + газ TON)
    if ton_to_usdt_spot_fee_percent >= 1.0 or ton_to_usdt_spot_fee_percent < 0:
        print("Ошибка: Процент спотовой комиссии должен быть между 0 и 1.")
        return None

    usd_after_ton_spot_fee = required_usdt_net / (1 - ton_to_usdt_spot_fee_percent)

    if ton_network_fee_percent >= 1.0 or ton_network_fee_percent < 0:
        print("Ошибка: Процент сетевой комиссии TON должен быть между 0 и 1.")
        return None

    usd_total_required = usd_after_ton_spot_fee / (1 - ton_network_fee_percent)

    # 5. Сколько Stars требуется
    num_stars = math.ceil(usd_total_required / telegram_star_to_usd_equivalent)

    print(f"\n--- Детализация расчета ---")
    # print(f"Исходная цена услуги (RUB): {service_price_rub:.2f} RUB")
    # print(f"Необходимая чистая сумма USDT (для получения {service_price_rub} RUB): {required_usdt_net:.4f} USDT")
    # print(f"USDT с учетом комиссии спота TON/USDT: {usd_after_ton_spot_fee:.4f} USD")
    # print(f"через USDT с учетом комиссии за газ TON: {usd_total_required:.4f} USD")
    # print(f"\nИтоговая цена в Telegram Stars: {num_stars} Stars")

    return int(num_stars)




