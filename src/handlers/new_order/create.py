from typing import List

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.localisation.texts import messages
from core.storage import storage
from loader import bot
from utils import callback_templates, states

template = callback_templates.services()


async def start_creating_new_order(lang, key: StorageKey, state: FSMContext, service_info):
    service_id = service_info['service_id']
    rate = service_info['rate']
    profit = service_info['profit']
    min_count = service_info['min_count']
    max_count = service_info['max_count']

    msg = messages.ask_quantity[lang].format(min_value=min_count, max_value=max_count)
    service_msg = await bot.send_message(key.chat_id, msg)
    await storage.set_data(key, service_id=service_id, rate=rate, profit=profit, min_value=min_count, max_value=max_count,
                           service_msg_ids=[service_msg.message_id], hot_order=False)
    await state.set_state(states.NewOrder.choosing_quantity)


async def start_creating_new_hot_order(lang, key: StorageKey, state: FSMContext, service_info):
    services_and_amount = service_info['services_and_amount']
    price = service_info['price']

    service_msg = await bot.send_message(key.chat_id, messages.ask_url[lang])
    await storage.set_data(key, services_and_amount=services_and_amount, total_amount=price, service_msg_ids=[service_msg.message_id], hot_order=True)
    await state.set_state(states.NewOrder.waiting_for_url)
