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
SUBSCRIPTION_SERVICE_262_ID = '262'
DEFAULT_SUBSCRIPTION_POSTS_MIN = 1
SUBSCRIPTION_SERVICE_262_POSTS_MIN = 3


def normalize_service_id(service_id: int | str) -> str:
    return str(service_id)


def get_subscription_posts_min(service_id: int, provider_service_type: str) -> int:
    if provider_service_type != api.SUBSCRIPTIONS_PROVIDER_SERVICE_TYPE:
        return DEFAULT_SUBSCRIPTION_POSTS_MIN
    if normalize_service_id(service_id) == SUBSCRIPTION_SERVICE_262_ID:
        return SUBSCRIPTION_SERVICE_262_POSTS_MIN
    return DEFAULT_SUBSCRIPTION_POSTS_MIN


async def start_creating_new_order(lang, key: StorageKey, state: FSMContext, service_info):
    service_id = service_info['service_id']
    service_name = service_info['service_name']
    old_rate = service_info['old_rate']
    rate = service_info['rate']
    min_count = service_info['min_count']
    max_count = service_info['max_count']
    provider_service_type = service_info.get('provider_service_type', api.DEFAULT_PROVIDER_SERVICE_TYPE)
    subscription_posts_min = get_subscription_posts_min(service_id, provider_service_type)

    if provider_service_type == api.SUBSCRIPTIONS_PROVIDER_SERVICE_TYPE:
        msg = messages.ask_subscription_posts[lang].format(min_value=subscription_posts_min)
        next_state = states.NewOrder.choosing_subscription_posts
    else:
        msg = messages.ask_quantity[lang].format(min_value=min_count, max_value=max_count)
        next_state = states.NewOrder.choosing_quantity

    service_msg = await bot.send_message(key.chat_id, msg)
    await storage.set_data(
        key,
        service_id=service_id,
        service_name=service_name,
        provider_service_type=provider_service_type,
        subscription_posts_min=subscription_posts_min,
        old_rate=old_rate,
        rate=rate,
        min_value=min_count,
        max_value=max_count,
        canceling_is_available=service_info.get('canceling_is_available'),
        service_msg_ids=[service_msg.message_id],
    )
    await state.set_state(next_state)

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
