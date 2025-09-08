from datetime import datetime

from core.db import admin
from utils.currency_api import get_actual_usdt_price


def to_rub_rate():
    exchange_rates: dict = admin.get_exchange_rates()
    usdt_rate_from_db = exchange_rates.get('usdt_to_rub_rate')
    updated_at = exchange_rates.get('updated_at')

    # formatted_updated_at = datetime.strptime(updated_at, admin.default_datetime_format)

    # TODO: удалить поддержку старого формата после обновления базы данных
    try:
        # Попытка распарсить с новым форматом
        formatted_updated_at = datetime.strptime(updated_at, admin.default_datetime_format)
    except ValueError:
        # Если новый формат не подходит, пробуем старый
        formatted_updated_at = datetime.strptime(updated_at, '%d-%m-%Y %H:%M')

    current_datetime = datetime.now()
    update_interval_in_seconds = exchange_rates.get('update_interval_in_seconds')
    needs_update = (current_datetime - formatted_updated_at).total_seconds() >= update_interval_in_seconds

    if usdt_rate_from_db > 0 and not needs_update:
        r = usdt_rate_from_db
    else:
        r = get_actual_usdt_price()
        admin.update_exchange_rates(r)
    return r

