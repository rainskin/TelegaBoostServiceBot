import datetime
from random import randint

from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users, orders
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import api
from utils.states import NewOrder, Payment


# current_data =
#
# service_id
# "97"
# rate
# 750
# min_value
# 1
# max_value
# # 10000
# total_amount
# 111
# quantity
# 245
# service_msg_ids
# [6548, ..., ..., ..., ..., ..., ...]
# url
# t.me/...

async def create_order(key: StorageKey, data: dict):
    user_id = key.user_id
    quantity = data['quantity']
    url = data['url']
    service_id: str = data['service_id']
    total_amount = data['total_amount']

    platform = users.get_user_platform(user_id)

    default_datetime_format = '%d-%m-%Y %H:%M'
    current_datetime = datetime.datetime.now().strftime(default_datetime_format)

    order_info = {
        'date': current_datetime,
        'service_id': service_id,
        'url': url,
        'quantity': quantity,
        'total_amount': total_amount
    }

    order_id = await api.create_new_order(user_id, service_id, url, quantity)
    print(f'Оформил заказ номер {order_id}')
    orders.new_order(user_id, platform, order_id, order_info)

    return order_id


@dp.callback_query(F.data == 'payment_method_internal_balance', Payment.choosing_method)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    lang = users.get_user_lang(user_id)
    data = await storage.get_data(key)
    total_amount: float = data['total_amount']
    user_balance = users.get_balance(user_id)
    currency = 'RUB'

    await query.answer()

    if user_balance >= total_amount:
        order_id = await create_order(key, data)
        current_balance = user_balance - total_amount
        users.update_balance(user_id, current_balance)
        message = messages.order_is_created[lang].format(order_id=order_id, currency=currency,
                                                         total_amount=total_amount, current_balance=current_balance)
        await query.message.delete()

    else:
        message = messages.not_enough_money[lang].format(current_balance=user_balance, currency=currency)

    await query.message.answer(message)
    service_msg_ids: list = data['service_msg_ids']

    await storage.delete_data(key)
    await bot.delete_messages(key.chat_id, service_msg_ids)
