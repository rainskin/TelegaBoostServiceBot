import asyncio
import datetime

import config
from core.db import admin, users
from core.db import orders as orders_db
from core.localisation.texts import messages
from loader import bot
from utils import api


def try_get_orders_for_execution() -> dict | None:
    orders_to_execution = admin.get_orders_for_execution()
    if orders_to_execution:
        return orders_to_execution

    orders_queue = admin.get_orders_queue()
    if orders_queue:
        admin.move_orders_to_execution_queue(orders_queue)
    return orders_queue


def get_total_amount(orders: dict) -> float:
    total_amount = 0.0
    for order_info in orders.values():
        total_amount += order_info.get('amount_without_commission')
    return total_amount


def get_summary_text(orders: dict, available_balance: float) -> str:
    total_amount = 0
    total_spent_by_users = 0.0
    total_profit = 0.0
    total_orders = 0

    for order_id, order_info in orders.items():
        total_amount += order_info['amount_without_commission']
        total_spent_by_users += order_info['total_amount']
        total_profit += order_info['profit']
        total_orders += 1


    text = (f'<b>Текущая очередь заказов</b>\n\n'
            f'<b>Всего заказов:</b> {total_orders}\n'
            f'<b>Текущий баланс:</b> {available_balance}\n'
            f'<b>Для оплаты необходимо:</b> {round(total_amount, 2)}\n'
            f'<b>Потрачено пользователями:</b> {total_spent_by_users:.2f}\n'
            f'<b>Прибыль:</b> {round(total_profit, 2)}')

    return text


async def create_order(internal_order_id: str, order_info: dict):
    quantity = order_info['quantity']
    service_id = order_info['service_id']
    user_id = order_info['user_id']
    url = order_info['url']
    platform = users.get_user_platform(user_id)

    default_datetime_format = '%d-%m-%Y %H:%M'
    current_datetime = datetime.datetime.now().strftime(default_datetime_format)
    order_info['execution_date'] = current_datetime
    order_info['internal_order_id'] = internal_order_id

    order_id = await api.create_new_order(user_id, service_id, url, quantity)
    orders_db.new_order(user_id, platform, order_id, order_info)

    return order_id


async def send_notification_to_user(user_id, order_id):
    lang = users.get_user_lang(user_id)
    text = messages.take_order_into_work[lang].format(order_id=order_id)
    await bot.send_message(user_id, text)


async def take_orders_into_work(orders: dict):
    count = 0
    non_active_users_number = 0
    total_amount = 0.0
    available_balance = await api.get_account_balance()
    for internal_order_id, order_info in orders.items():
        user_id = order_info.get('user_id')
        amount = order_info.get('amount_without_commission')

        order_id = await create_order(internal_order_id, order_info)

        admin.remove_order_from_execution_queue(internal_order_id)
        orders_db.remove_not_accepted_order(user_id, internal_order_id)

        try:
            await send_notification_to_user(user_id, order_id)
        except Exception as e:
            non_active_users_number += 1
            print(f"Error sending notification to user {user_id}: {e}")
        count += 1
        total_amount += amount

    non_active_users_stats_text = f'Заблокировали бота: {non_active_users_number}' if non_active_users_number > 0 else ''
    text = f'Оформил {count} заказ(ов)\n\n{non_active_users_stats_text}\n\nПредполагаемый остаток на балансе:{available_balance-total_amount}'
    await send_report_to_admin(text)


async def send_report_to_admin(text):
    await bot.send_message(config.ADMIN_ID, text)


async def try_take_orders_into_work():
    orders = try_get_orders_for_execution()
    if not orders:
        return

    available_balance = await api.get_account_balance()
    text = get_summary_text(orders, available_balance)
    await send_report_to_admin(text)

    total_amount = get_total_amount(orders)
    available_balance = await api.get_account_balance()

    if total_amount > available_balance:
        text = (f'<b>Недостаточно средств.</b>\n'
                f'Текущий баланс: <b>{available_balance:.2f} руб.</b>\n'
                f'Необходимо пополнить счет еще минимум на <b>{round((total_amount - available_balance), 2)} руб.</b>')
        await send_report_to_admin(text)
        return

    await take_orders_into_work(orders)


async def try_take_orders_into_work_repeatedly(cooldown: int = 60):
    while True:
        await try_take_orders_into_work()
        await asyncio.sleep(cooldown)
