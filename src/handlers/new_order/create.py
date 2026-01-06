import datetime

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

import config
from core.db import orders, users, admin
from core.db.models.order_item import OrderItem
from core.db.main_orders_queue import orders_queue
from core.localisation.texts import messages
from core.storage import storage
from enums.orders.service_type import ServiceType
from loader import bot
from utils import callback_templates, states, api

template = callback_templates.services()


async def start_creating_new_order(lang, key: StorageKey, state: FSMContext, service_info):
    service_id = service_info['service_id']
    service_name = service_info['service_name']
    old_rate = service_info['old_rate']
    rate = service_info['rate']
    min_count = service_info['min_count']
    max_count = service_info['max_count']

    msg = messages.ask_quantity[lang].format(min_value=min_count, max_value=max_count)
    service_msg = await bot.send_message(key.chat_id, msg)
    await storage.set_data(key, service_id=service_id, service_name=service_name, old_rate=old_rate, rate=rate, min_value=min_count,
                           max_value=max_count,
                           service_msg_ids=[service_msg.message_id])
    await state.set_state(states.NewOrder.choosing_quantity)

async def save_unpaid_order(order_item: OrderItem):
    await orders_queue.save(order_item)

# async def place_order(user_id: int, internal_order_id: str, data: dict, payment_method: str):
#     data['payment_method'] = payment_method
#
#     admin.put_order_to_queue(user_id, internal_order_id, data)
#
#     await bot.send_message(config.ADMIN_ID, f'🤑 Новый заказ. Сумма {data["total_amount"]}')


async def place_order(order_item: OrderItem):
    await admin.put_order_to_queue(order_item)
