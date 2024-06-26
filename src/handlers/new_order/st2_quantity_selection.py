from aiogram import types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import states
from utils.keyboards import navigation_kb


@dp.message(F.content_type == ContentType.TEXT, states.NewOrder.choosing_quantity)
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    lang = users.get_user_lang(user_id)
    chat_id = msg.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    min_value = data['min_value']
    max_value = data['max_value']
    rate = data['rate']
    old_rate = data['old_rate']
    service_msg_ids: list = data['service_msg_ids']

    try:
        value = int(msg.text)
    except ValueError as e:
        service_msg = await msg.answer(
            messages.value_is_not_number[lang].format(min_value=min_value, max_value=max_value))
        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, service_msg_ids=service_msg_ids)
        return

    if not is_valid_quantity(value, min_value, max_value):

        service_msg = await msg.answer(messages.wrong_quantity[lang].format(min_value=min_value, max_value=max_value))
        service_msg_ids.append(service_msg.message_id)

    else:
        total_amount = get_amount_by_rate_and_quantity(rate, value)
        amount_without_commission = get_amount_by_rate_and_quantity(old_rate, value)
        profit = total_amount - amount_without_commission
        currency = 'RUB'
        service_msg = await msg.answer(messages.valid_quantity[lang].format(total_cost=total_amount, currency=currency),
                                       reply_markup=navigation_kb.order_navigation(lang).as_markup())
        if service_msg_ids:
            await bot.delete_messages(chat_id, service_msg_ids)
            service_msg_ids = []

        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, quantity=value, total_amount=total_amount, amount_without_commission=amount_without_commission, profit=profit)

    await storage.update_data(key, service_msg_ids=service_msg_ids)


def is_valid_quantity(value: int, min_value: int, max_value: int):
    return min_value <= value <= max_value

def get_amount_by_rate_and_quantity(rate: int, quantity: int):
    return round((quantity * rate / 1000), 2)
