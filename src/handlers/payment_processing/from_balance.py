from aiogram import F, types
from aiogram.fsm.storage.base import StorageKey

from core.db import users, orders
from core.localisation.texts import messages
from core.localisation.texts.messages import not_enough_money
from core.storage import storage
from handlers.new_order.create import place_order
from loader import dp, bot
from utils import navigation
from utils.states import Payment


@dp.callback_query(F.data == 'payment_method_internal_balance', Payment.choosing_method)
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    lang = users.get_user_lang(user_id)
    data = await storage.get_data(key)
    hot_order = data['hot_order']
    internal_order_id = data['internal_order_id']
    total_amount: float = data['total_amount']
    user_balance = users.get_balance(user_id)
    currency = 'RUB'
    service_msg_ids: list = data['service_msg_ids']
    await query.answer()

    if user_balance >= total_amount:
        current_balance = user_balance - total_amount
        await place_order(user_id, internal_order_id, hot_order, data, payment_method='internal_balance')
        message = (f'{messages.order_is_created[lang].format(order_id=internal_order_id)}'
                   f'{messages.spent_amount_from_balance[lang].format(currency=currency, total_amount=total_amount, current_balance=current_balance)}')
        orders.reset_last_order_info(user_id)
        await query.message.answer(message)

        if service_msg_ids:
            await bot.delete_messages(user_id, service_msg_ids)

            users.update_balance(user_id, current_balance)
            await storage.delete_data(key)
            await navigation.return_to_menu(user_id)
            await bot.delete_messages(key.chat_id, service_msg_ids)

    else:
        await query.message.answer(not_enough_money[lang].format(current_balance=user_balance, currency=currency))


