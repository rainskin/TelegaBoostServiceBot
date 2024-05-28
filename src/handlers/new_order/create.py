from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.localisation.texts import messages
from core.storage import storage
from loader import bot
from utils import callback_templates, states

template = callback_templates.services()


async def start_creating_new_order(lang, key: StorageKey, state: FSMContext, service_id: str, rate, min_count,
                                   max_count):
    print(type(rate), type(min_count))
    msg = messages.ask_quantity[lang].format(min_value=min_count, max_value=max_count)
    service_msg = await bot.send_message(key.chat_id, msg)
    await storage.set_data(key, service_id=service_id, rate=rate, min_value=min_count, max_value=max_count,
                           service_msg_ids=[service_msg.message_id])
    await state.set_state(states.NewOrder.choosing_quantity)


