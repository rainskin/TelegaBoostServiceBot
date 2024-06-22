from typing import List

from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from config import ADMIN_ID
from core.db import users, orders
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils.keyboards import payment_methods
from utils.states import NewOrder, Payment


@dp.callback_query(F.data == 'make_order', NewOrder.waiting_for_url)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    chat_id = query.message.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    service_msg_ids: list = data['service_msg_ids']

    total_amount = data['total_amount']
    currency = 'RUB'

    await query.answer()
    user_balance = users.get_balance(user_id)
    if service_msg_ids:
        await bot.delete_messages(chat_id, service_msg_ids)
        service_msg_ids = []

    kb = payment_methods.kb(lang, from_balance=True)

    text = messages.select_payment_method[lang].format(total_amount=total_amount,
                                                       currency=currency, current_balance=user_balance)
    msg = await query.message.answer(text, reply_markup=kb.as_markup())
    await state.set_state(Payment.choosing_method)

    service_msg_ids.append(msg.message_id)
    internal_order_id = await get_internal_order_id(user_id)
    orders.save_last_order_info(user_id, data)
    await storage.update_data(key, internal_order_id=internal_order_id)


async def get_internal_order_id(user_id: int):
    internal_order = orders.get_last_internal_order(user_id)
    template = f'{user_id}_N0017'
    if internal_order:
        order_number = int(internal_order.replace(template, ''))
        new_internal_order = order_number + 1

    else:
        active_orders = orders.get_current_orders(user_id)
        orders_in_archive = orders.get_orders_from_archive(user_id)

        amount_active_orders = len(active_orders) if active_orders else 0
        amount_archive_orders = len(orders_in_archive) if orders_in_archive else 0

        total_orders = amount_active_orders + amount_archive_orders
        new_internal_order = total_orders + 1

    result = f'{template}{new_internal_order}'
    orders.update_last_internal_order(user_id, result)
    return result
