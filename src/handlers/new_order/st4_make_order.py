
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users, orders
from core.db.models.order_item import OrderItem
from core.localisation.texts.unpaid_order_summary import STANDARD_ORDER
from core.storage import storage
from enums.orders.service_type import ServiceType
from handlers.new_order.create import save_unpaid_order
from loader import dp, bot
from utils.keyboards.unpaid_orders import get_keyboard
from utils.methods import delete_messages
from utils.states import NewOrder


@dp.callback_query(F.data == 'make_order', NewOrder.waiting_for_url)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    chat_id = query.message.chat.id
    key = StorageKey(bot.id, chat_id, user_id)

    # total_amount = data['total_amount']
    currency = 'RUB'

    await query.answer()

    internal_order_id = await get_internal_order_id(user_id)
    await storage.update_data(key, internal_order_id=internal_order_id)
    data = await storage.get_data(key)
    text = get_order_summary_text(lang, data, currency)

    kb = get_keyboard(lang, internal_order_id)
    await query.message.answer(text, reply_markup=kb.as_markup())

    service_msg_ids: list = data['service_msg_ids']

    order_item = OrderItem(
        internal_order_id=data.get('internal_order_id'),
        user_id=user_id,
        service_type=ServiceType.STANDARD,
        service_id=data.get('service_id'),
        service_name=data.get('service_name'),
        url=data.get('url'),
        quantity=data.get('quantity'),
        amount_without_commission=data.get('amount_without_commission'),
        total_amount=data.get('total_amount'),
        profit=data.get('profit')
    )

    save_unpaid_order(order_item)
    await state.set_state(None)
    await storage.reset_data(key)
    await delete_messages(chat_id, service_msg_ids)


#  ---------------
#    OLD VERSION
#  ---------------

# @dp.callback_query(F.data == 'make_order', NewOrder.waiting_for_url)
# async def _(query: types.CallbackQuery, state: FSMContext):
#     print('make order handler...')
#     user_id = query.from_user.id
#     lang = users.get_user_lang(user_id)
#     chat_id = query.message.chat.id
#     key = StorageKey(bot.id, chat_id, user_id)
#     data = await storage.get_data(key)
#     service_msg_ids: list = data['service_msg_ids']
#
#     total_amount = data['total_amount']
#     currency = 'RUB'
#
#     await query.answer()
#     user_balance = users.get_balance(user_id)
#     if service_msg_ids:
#         await bot.delete_messages(chat_id, service_msg_ids)
#         service_msg_ids = []
#
#     kb = payment_methods.kb(lang, from_balance=True)
#
#     text = messages.confirm_order_payment[lang].format(total_amount=total_amount,
#                                                        currency=currency, current_balance=user_balance)
#     msg = await query.message.answer(text, reply_markup=kb.as_markup())
#     await state.set_state(Payment.choosing_method)
#
#     service_msg_ids.append(msg.message_id)
#     internal_order_id = await get_internal_order_id(user_id)
#     await storage.update_data(key, internal_order_id=internal_order_id)
#     data = await storage.get_data(key)
#     save_unpaid_order(user_id, ServiceType.STANDARD, data)




    # orders.save_last_order_info(user_id, data)  # сохранение неиспользуемых в дальнейшем данных. Удалить после проверки, что ничего не ломается.

# --------------- Current Data ---------------
    #     "service_id": "213",
    #     "service_name": "Love❤️ | Telegram Reaction | +Просмотры",
    #     "old_rate": 650,
    #     "rate": 780,
    #     "min_value": 1,
    #     "max_value": 40000,
    #     "service_msg_ids": [15843, 15848],
    #     "quantity": 22,
    #     "total_amount": 17.16,
    #     "amount_without_commission": 14.3,
    #     "profit": 2.86,
    #     "url": "https://site.com",
    #     "internal_order_id": "936845322_N001768",



async def get_internal_order_id(user_id: int):
    internal_order = orders.get_last_internal_order(user_id)
    template = f'{user_id}_N0017'
    if internal_order:
        order_number = int(internal_order.replace(template, ''))
        new_internal_order = order_number + 1
    else:
        new_internal_order = 1

    result = f'{template}{new_internal_order}'
    orders.update_last_internal_order(user_id, result)
    return result


def get_order_summary_text(lang: str, order_data: dict, currency: str) -> str:
    text = STANDARD_ORDER[lang].format(
        internal_order_id=order_data.get('internal_order_id'),
        service_name=order_data.get('service_name'),
        quantity=order_data.get('quantity'),
        url=order_data.get('url'),
        total_amount=order_data.get('total_amount'),
        currency=currency
    )

    return text
