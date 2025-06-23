from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from busines_logic.calculate_commission import get_amount_minus_commission
from busines_logic.referrals_managment import add_referral_reward
from core.db import users, orders, admin
from core.db.admin import build_payment_info
from core.localisation.texts import messages
from core.storage import storage
from handlers.new_order.create import place_order
from handlers.new_order.st4_make_order import get_internal_order_id
from loader import dp, bot
from utils import callback_templates, navigation, states
from utils.Payment_methods.aaio.methods import get_payment_url, check_payment_status
from utils.Payment_methods.aaio.payment_statuses import current_payment_status_translated
from utils.keyboards.payment_methods import card_payment
from utils.states import Payment




@dp.callback_query(F.data == 'payment_method_card', Payment.choosing_method)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id

    key = StorageKey(bot.id, user_id, user_id)
    lang = users.get_user_lang(user_id)

    data = await storage.get_data(key)
    amount = data.get('amount')
    amount_with_commission = data.get('amount_with_commission')

    currency = data.get('currency')
    internal_order_id = await get_internal_order_id(user_id)
    payment_id = f'P{internal_order_id}'
    text = messages.payment_by_card[lang].format(
        transaction_id=payment_id, amount=f'{amount_with_commission: .2f}', currency=currency,)

    payment_url = await get_payment_url(payment_id, amount, lang)
    payment_info = build_payment_info(user_id, amount_rub=amount_with_commission, currency='RUB', amount_original=amount,
                                      payment_url=payment_url, balance_recharge=True)

    admin.save_payment(payment_id, payment_info)

    kb = card_payment(lang, payment_url, payment_id, balance_recharge=True)
    await query.message.answer(text, reply_markup=kb.as_markup())
    await query.answer()
    await query.message.delete()
    await state.set_state(None)


    #
    # user_id = query.from_user.id
    # print(await bot.get_chat(user_id))
    # chat_id = query.message.chat.id
    # key = StorageKey(bot.id, chat_id, user_id)
    # lang = users.get_user_lang(user_id)
    # data: dict = await storage.get_data(key)
    # total_amount: float = data['amount']
    # internal_order_id = data['internal_order_id']
    # data['service_msg_ids'] = []
    #
    # payment_url = await get_payment_url(internal_order_id, total_amount, lang)
    # await query.answer()
    #
    # kb = card_payment(lang, payment_url, internal_order_id)
    # await query.message.answer(messages.payment_by_card[lang].format(order_id=internal_order_id),
    #                            reply_markup=kb.as_markup())
    # await state.set_state(None)
    # await query.message.delete()

# @dp.callback_query(F.data == 'yes', states.BalanceRecharge.choosing_amount)
# async def _(query: types.CallbackQuery, state: FSMContext):
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
#     payment_info = await get_payment_info(user_id, amount, payment_url, balance_recharge=True)
#
#     admin.save_payment(payment_id, payment_info)
#
#     kb = card_payment(lang, payment_url, payment_id, balance_recharge=True)
#     await query.message.answer(text, reply_markup=kb.as_markup())
#     await query.answer()
#     await query.message.delete()
#     await state.set_state(states.BalanceRecharge.choosing_amount)

#
# @dp.callback_query(F.data == 'payment_method_card', Payment.choosing_method)
# async def _(query: types.CallbackQuery, state: FSMContext):
#     user_id = query.from_user.id
#     print(await bot.get_chat(user_id))
#     chat_id = query.message.chat.id
#     key = StorageKey(bot.id, chat_id, user_id)
#     lang = users.get_user_lang(user_id)
#     data: dict = await storage.get_data(key)
#     total_amount: float = data['amount']
#     internal_order_id = data['internal_order_id']
#     data['service_msg_ids'] = []
#
#     payment_url = await get_payment_url(internal_order_id, total_amount, lang)
#     await query.answer()
#
#     kb = card_payment(lang, payment_url, internal_order_id)
#     await query.message.answer(messages.payment_by_card[lang].format(order_id=internal_order_id),
#                                reply_markup=kb.as_markup())
#     await state.set_state(None)
#     await query.message.delete()

#
# template = callback_templates.check_payment()
#
#
# @dp.callback_query(F.data.startswith(template))
# async def _(query: types.CallbackQuery, state: FSMContext):
#     user_id = query.from_user.id
#     lang = users.get_user_lang(user_id)
#     internal_order_id = query.data.replace(template, '')
#     data = orders.get_last_order_info(user_id)
#     status = await check_payment_status(user_id, internal_order_id)
#     status_msg_ids = []
#
#     if data and internal_order_id == data['internal_order_id']:
#         if not status:
#             await query.answer()
#             return
#
#         if status != 'success' and status != 'hold':
#             text = (f'{messages.current_payment_status[lang]}:\n\n'
#                     f'{current_payment_status_translated[status][lang]}')
#
#             msg = await query.message.answer(text)
#             status_msg_ids.append(msg.message_id)
#             await query.answer()
#             return
#
#         if status == 'success' or status == 'hold':
#             hot_order = data['hot_order']
#             await place_order(user_id, internal_order_id, hot_order, data, payment_method='card')
#             message = f'{messages.order_is_created[lang].format(order_id=internal_order_id)}'
#             orders.reset_last_order_info(user_id)
#
#             await query.message.answer(message)
#             await query.message.delete()
#             await navigation.return_to_menu(user_id, state)
#             if status_msg_ids:
#                 await bot.delete_messages(user_id, status_msg_ids)
#
#     else:
#         message = messages.some_error_try_again[lang]
#         await query.message.answer(message)
#
#     await query.answer()

# Check Payment

template = callback_templates.balance_recharge()


@dp.callback_query(F.data.startswith(template))
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    payment_id = query.data.replace(template, '')

    status = await check_payment_status(user_id, payment_id)
    status = 'success'
    status_msg_ids = []

    if not status:
        await query.answer()
        return

    if status != 'success' and status != 'hold':
        text = (f'{messages.current_payment_status[lang]}:\n\n'
                f'{current_payment_status_translated[status][lang]}')

        msg = await query.message.answer(text)
        status_msg_ids.append(msg.message_id)
        await query.answer()
        return

    if not admin.is_not_paid(payment_id):
        text = messages.balance_recharge_already_paid[lang]
        await query.message.answer(text)
        await query.message.delete()
        return

    payment_info = admin.get_payment_info(payment_id)

    if payment_info:
        amount = payment_info.get('amount_rub')
        print(amount)

        recharge_commission = admin.get_balance_recharge_commission()
        # if recharge_commission:
        #     amount = await get_amount_minus_commission(amount, recharge_commission)
        # else:
        #     amount = amount

        await add_balance(user_id, amount)
        admin.update_payment_status(payment_id, status)
        admin.move_to_successful_payments(payment_id)
        currency = 'RUB'

        formatted_amount = f'{amount:.2f}'
        await query.message.answer(
            messages.balance_recharge_successfully_paid[lang].format(amount=formatted_amount, currency=currency))
        await query.message.delete()

    if status_msg_ids:
        await bot.delete_messages(user_id, status_msg_ids)

    await navigation.return_to_menu(user_id, state)
    await query.answer()


async def add_balance(user_id: int, amount: float):
    users.add_balance(user_id, amount)
    inviter_id = users.get_inviter_id(user_id)
    if inviter_id:
        await add_referral_reward(inviter_id, amount)