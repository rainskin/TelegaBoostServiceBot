import asyncio

import aiohttp
import requests

import config
from core.db import admin, users
from core.db import orders as orders_db
from core.db.main_orders_queue import orders_queue
from core.db.models.order_item import OrderItem
from core.localisation.texts import messages
from enums.orders.order_status import OrderStatus
from loader import bot

API_KEY = config.TG_STARS_API_KEY
BASE_URL = config.TG_STARS_API_BASE_URL
# BASE_URL = 'http://127.0.0.1:8000/api/v1'


async def get_ton_balance():
    header = {'X-API-KEY': API_KEY}
    body = {'in_ton': True}
    method = 'get_balance'
    url = f'{BASE_URL}/{method}'

    for attempt in range(1, 4):  # 3 попытки
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=header, json=body, timeout=50) as response:
                    response.raise_for_status()
                    return await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < 3:
                error_message = (
                    f"❌ Ошибка HTTP-запроса к stars-api при запросе баланса (попытка {attempt}).\n"
                    f"Ошибка: {str(e)}"
                )
                await bot.send_message(chat_id=config.ADMIN_ID, text=error_message)
                await asyncio.sleep(5 * attempt)
                continue
            return None

        except Exception:
            return None

async def buy_stars(recipient: str, amount: int) -> dict:
    header = {'X-API-KEY': API_KEY}
    body = {'recipient': recipient, 'amount': amount}
    url = f'{BASE_URL}/buy_stars'

    for attempt in range(1, 4):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=header, json=body, timeout=100) as response:
                    try:
                        data = await response.json()
                    except Exception:
                        data = {"error": f"Failed to parse JSON, status={response.status}", "status": response.status}

                    if response.status >= 400:
                        # возвращаем тело ошибки, чтобы process_tg_stars_order мог обработать
                        return data

                    return data

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < 3:
                await bot.send_message(config.ADMIN_ID,
                                       f"❌ Ошибка HTTP-запроса к stars-api (попытка {attempt}): {str(e)}")
                await asyncio.sleep(5 * attempt)
                continue
            return {"error": str(e)}

        except Exception as e:
            return {"error": str(e)}


async def process_tg_stars_order(order_item: OrderItem):
    result = await buy_stars(order_item.url, order_item.quantity)
    print(result)
    # result = {'Successful': True}
    # result = {'error': 'Not enough balance'}
    # result = {'error': 'No Telegram users found'}
    lang = users.get_user_lang(order_item.user_id)
    orders_db.new_order('telegram', order_item)
    if not result:
        error_message = f"⚠️ Не удалось купить звезды. Заказ {order_item.internal_order_id}. Ответ от API: {result}"
        raise OrderProcessingError(error_message)

    if 'error' in result:
        error_message = result.get('error')
        if 'Not enough balance' in error_message:
            raise InsufficientBalanceError(
                f"⚠️ Недостаточно средств для покупки звезд. Заказ {order_item.internal_order_id}, количество звезд {order_item.total_amount}")

        elif 'PaymentGetInfoError' in result:
            raise OrderProcessingError(f'⚠️ Ошибка PaymentGetInfoError при попытке купить звезды. Заказ {order_item.internal_order_id}')

        elif 'No Telegram users found' in error_message:
            order_item.order_status = OrderStatus.CANCELED
            order_item.deleted = True
            order_item.is_money_returned = True
            orders_queue.update(order_item)
            order_item = orders_queue.get(order_item.internal_order_id)

            admin.remove_order_from_execution_queue(order_item.internal_order_id)
            orders_db.return_money_for_current_order(order_item.user_id, order_item.internal_order_id,
                                                     order_item.total_amount)
            orders_db.update_active_order(order_item.internal_order_id, order_item)
            orders_db.move_orders_to_archive(order_item.user_id, order_item.internal_order_id)
            orders_db.remove_not_accepted_order(order_item.user_id, order_item.internal_order_id)
            text = messages.tg_stars_order_invalid_username[lang].format(internal_order_id=order_item.internal_order_id)
            await bot.send_message(chat_id=order_item.user_id, text=text)

            error_message = f'Заказ на звезды {order_item.internal_order_id} отменен. Invalid username'
            raise InvalidUsernameError(error_message)

        else:
            raise OrderProcessingError(error_message)

    elif 'Successful' in result:
        successful = result.get('Successful')
        if successful:
            order_item.order_status = OrderStatus.COMPLETED
            orders_queue.update(order_item)
            order_item = orders_queue.get(order_item.internal_order_id)

            admin.remove_order_from_execution_queue(order_item.internal_order_id)
            orders_db.remove_not_accepted_order(order_item.user_id, order_item.internal_order_id)
            orders_db.update_active_order(order_item.internal_order_id, order_item)
            orders_db.move_orders_to_archive(order_item.user_id, order_item.internal_order_id)
            text = messages.tg_stars_order_completed[lang].format(internal_order_id=order_item.internal_order_id,
                                                                  amount=order_item.quantity,
                                                                  username=order_item.url)
            await bot.send_message(chat_id=order_item.user_id, text=text)
        else:
            error_message = f"⚠️ При попытке купить звезды не удалось отправить транзакцию. Заказ {order_item.internal_order_id}"
            raise OrderExecutionError(error_message)

    else:
        raise OrderProcessingError(f'Неизвестная ошибка при попытке купить звезды. Ответ АПИ:\n{result}')

    # print(f"Skipping non-standard service type for order {order_item.internal_order_id}")
    # order_item.order_status = OrderStatus.CANCELED
    # order_item.deleted = True
    # orders_queue.update(order_item)
    # admin.remove_order_from_execution_queue(order_item.internal_order_id)
    # orders_db.remove_not_accepted_order(order_item.user_id, order_item.internal_order_id)


def calculate_price_rub(stars: int) -> int:
    """
    Рассчитывает цену в рублях, прибыль и маржу за заданное количество звёзд,
    с учётом курса доллара к рублю.
    """
    # Таблица диапазонов: (минимум звёзд, цена за 1 звезду в рублях)
    price_ranges = admin.get_tg_stars_price_ranges_in_rub()

    price_per_star = price_ranges[0][1]
    for min_stars, rub_price in price_ranges:
        if stars >= min_stars:
            price_per_star = rub_price
        else:
            break

    total_price = int(stars * price_per_star)
    return total_price


class OrderProcessingError(Exception):
    """Базовое исключение при обработке заказа"""


class InsufficientBalanceError(OrderProcessingError):
    """Недостаточно средств выполнения заказа"""


class InvalidUsernameError(OrderProcessingError):
    """Неверно указан юзернейм для получения звёзд"""


class OrderExecutionError(OrderProcessingError):
    """Ошибка выполнения заказа"""
