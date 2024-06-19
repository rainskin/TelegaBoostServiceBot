import datetime
from typing import List

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import orders, users, admin
from core.localisation.texts import messages
from core.storage import storage
from loader import bot
from utils import callback_templates, states, api

template = callback_templates.services()


async def start_creating_new_order(lang, key: StorageKey, state: FSMContext, service_info):
    service_id = service_info['service_id']
    old_rate = service_info['old_rate']
    rate = service_info['rate']
    min_count = service_info['min_count']
    max_count = service_info['max_count']

    msg = messages.ask_quantity[lang].format(min_value=min_count, max_value=max_count)
    service_msg = await bot.send_message(key.chat_id, msg)
    await storage.set_data(key, service_id=service_id, old_rate=old_rate, rate=rate, min_value=min_count,
                           max_value=max_count,
                           service_msg_ids=[service_msg.message_id], hot_order=False)
    await state.set_state(states.NewOrder.choosing_quantity)

async def start_creating_new_hot_order(lang, key: StorageKey, state: FSMContext, service_info):
    services_and_amount = service_info['services_and_amount']
    amount_without_commission = service_info['amount_without_commission']
    price = service_info['price']
    profit = service_info['profit']
    canceling_is_available = service_info['canceling_is_available']

    service_msg = await bot.send_message(key.chat_id, messages.ask_url[lang])
    await storage.set_data(key, services_and_amount=services_and_amount, total_amount=price,
                           service_msg_ids=[service_msg.message_id],
                           amount_without_commission=amount_without_commission,
                           profit=profit, canceling_is_available=canceling_is_available, hot_order=True)
    await state.set_state(states.NewOrder.waiting_for_url)

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
    orders.new_order(user_id, platform, order_id, order_info)

    return order_id


async def place_order(user_id: int, internal_order_id: str, hot_order: bool, data: dict, payment_method: str):
    data['payment_method'] = payment_method
    if not hot_order:
        admin.put_order_to_queue(user_id, internal_order_id, data)

    else:
        services_and_amount: dict = data['services_and_amount']
        url = data['url']
        for service_id, quantity in services_and_amount.items():
            data['service_id'] = service_id
            data['quantity'] = quantity
            data['url'] = url
            admin.put_order_to_queue(user_id, internal_order_id, data)
