from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users, orders, admin
from core.db.admin import build_payment_info
from core.localisation.texts import messages
from core.localisation.texts.messages import not_enough_money
from core.storage import storage
from handlers.new_order.create import place_order
from handlers.new_order.st4_make_order import get_internal_order_id
from loader import dp, bot
from utils import navigation, states
from utils.Payment_methods.aaio.methods import get_payment_url
from utils.keyboards import navigation_kb
from utils.keyboards.payment_methods import card_payment
from utils.states import Payment


# @dp.callback_query(F.data == 'payment_method_internal_balance', Payment.choosing_method)
# async def _(query: types.CallbackQuery, state: FSMContext):
#     user_id = query.from_user.id
#     chat_id = query.message.chat.id
#     key = StorageKey(bot.id, chat_id, user_id)
#     lang = users.get_user_lang(user_id)
#     data = await storage.get_data(key)
#     hot_order = data['hot_order']
#     internal_order_id = data['internal_order_id']
#     total_amount: float = data['total_amount']
#     user_balance = users.get_balance(user_id)
#     currency = 'RUB'
#     service_msg_ids: list = data['service_msg_ids']
#     await query.answer()
#
#     if user_balance >= total_amount:
#         current_balance = round((user_balance - total_amount), 2)
#         await place_order(user_id, internal_order_id, hot_order, data, payment_method='internal_balance')
#         message = (f'{messages.order_is_created[lang].format(order_id=internal_order_id)}'
#                    f'{messages.spent_amount_from_balance[lang].format(currency=currency, total_amount=total_amount, current_balance=current_balance)}')
#         orders.reset_last_order_info(user_id)
#         await query.message.answer(message)
#         await query.message.delete()
#
#         if service_msg_ids:
#             await bot.delete_messages(user_id, service_msg_ids)
#
#             users.update_balance(user_id, current_balance)
#             await storage.delete_data(key)
#             await navigation.return_to_menu(user_id, state)
#             await bot.delete_messages(key.chat_id, service_msg_ids)
#
#     else:
#         await query.message.answer(not_enough_money[lang].format(current_balance=user_balance, currency=currency),
#                                    reply_markup=navigation_kb.balance_recharge_button(lang).as_markup())
#


@dp.callback_query(F.data == 'payment_method_internal_balance', Payment.choosing_method)
async def _(query: types.CallbackQuery, state: FSMContext):
    print('Processing payment from internal balance...')
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
        current_balance = round((user_balance - total_amount), 2)
        await place_order(user_id, internal_order_id, hot_order, data, payment_method='internal_balance')
        message = (f'{messages.order_is_created[lang].format(order_id=internal_order_id)}'
                   f'{messages.spent_amount_from_balance[lang].format(currency=currency, total_amount=total_amount, current_balance=current_balance)}')
        orders.reset_last_order_info(user_id)
        await query.message.answer(message)
        await query.message.delete()

        if service_msg_ids:
            await bot.delete_messages(user_id, service_msg_ids)

            users.update_balance(user_id, current_balance)
            await storage.delete_data(key)
            await navigation.return_to_menu(user_id, state)
            await bot.delete_messages(key.chat_id, service_msg_ids)

    else:
        await query.message.answer(not_enough_money[lang].format(current_balance=user_balance, currency=currency),
                                   reply_markup=navigation_kb.balance_recharge_button(lang).as_markup())


# @dp.callback_query(F.data == 'yes', states.BalanceRecharge.choosing_amount)
# async def _(query: types.CallbackQuery, state: FSMContext):
#     print('Processing payment from balance...')
#     user_id = query.from_user.id
#
#     key = StorageKey(bot.id, user_id, user_id)
#     lang = users.get_user_lang(user_id)
#
#     data = await storage.get_data(key)
#     amount = data.get('amount')
#
#     internal_order_id = await get_internal_order_id(user_id)
#     payment_id = f'P{internal_order_id}'
#     text = messages.payment_by_card[lang].format(order_id=payment_id)
#     payment_url = await get_payment_url(payment_id, amount, lang)
#     payment_info = await build_payment_info(user_id, amount, payment_url, balance_recharge=True)
#
#     admin.save_payment(payment_id, payment_info)
#
#     kb = card_payment(lang, payment_url, payment_id, balance_recharge=True)
#     await query.message.answer(text, reply_markup=kb.as_markup())
#     await query.answer()
#     await query.message.delete()
#     await state.set_state(states.BalanceRecharge.choosing_amount)
#
#


