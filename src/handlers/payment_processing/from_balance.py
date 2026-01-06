from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from busines_logic.order_managment.place_paid_orders_to_que import place_paid_order
from core.db import users
from core.db.main_orders_queue import orders_queue
from core.db.models.order_item import OrderItem
from core.db.models.transaction_item import TransactionItem
from core.db.transactions import transactions
from core.localisation.texts import messages
from core.localisation.texts.messages import not_enough_money
from core.storage import storage
from enums.orders.order_status import OrderStatus
from enums.orders.payment_methods import PaymentMethod
from enums.transaction_type import TransactionType
from loader import dp, bot
from utils import navigation
from utils.keyboards import navigation_kb
from utils.states import Payment


# TODO: удалить старый закомментированный код после проверки работоспособности нового

# @dp.callback_query(F.data == 'payment_method_internal_balance', Payment.choosing_method)
# async def _(query: types.CallbackQuery, state: FSMContext):
#     print('Processing payment from internal balance...')
#     user_id = query.from_user.id
#     chat_id = query.message.chat.id
#     key = StorageKey(bot.id, chat_id, user_id)
#     lang = await users.get_user_lang(user_id)
#     data = await storage.get_data(key)
#     print(data)
#     internal_order_id = data['internal_order_id']
#     total_amount: float = data['total_amount']
#     user_balance = users.get_balance(user_id)
#     currency = 'RUB'
#     service_msg_ids: list = data['service_msg_ids']
#     await query.answer()
#
#     if user_balance >= total_amount:
#         current_balance = round((user_balance - total_amount), 2)
#         await place_order(user_id, internal_order_id, data, payment_method='internal_balance')
#         message = (f'{messages.order_is_created[lang].format(order_id=internal_order_id)}'
#                    f'{messages.spent_amount_from_balance[lang].format(currency=currency, total_amount=total_amount, current_balance=current_balance)}')
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
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    lang = await users.get_user_lang(user_id)
    data = await storage.get_data(key)
    internal_order_id = data['internal_order_id']
    message_with_order_info_id = data.get('message_with_order_info_id')
    order_item = await orders_queue.get(internal_order_id)
    total_amount: float = order_item.total_amount

    if order_item.deleted:
        await query.answer(messages.unpaid_order_was_deleted_early[lang], show_alert=True)
        await query.message.delete()
        return

    currency = 'RUB'
    await query.answer()
    user_balance = await users.get_balance(user_id)
    if user_balance >= total_amount:

        await pay_order(user_id, order_item)
        await place_paid_order(order_item)

        await query.message.answer(messages.order_is_paid[lang].format(internal_order_id=internal_order_id))
        await query.message.delete()

        if message_with_order_info_id:
            try:
                await bot.delete_message(chat_id=user_id, message_id=message_with_order_info_id)
            except Exception as e:
                pass

        await storage.delete_data(key)
        await navigation.return_to_menu(user_id, state)

    else:
        await query.message.answer(not_enough_money[lang].format(current_balance=user_balance, currency=currency),
                                   reply_markup=navigation_kb.balance_recharge_button(lang).as_markup())


@dp.callback_query(F.data == 'payment_method_internal_balance')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = await users.get_user_lang(user_id)

    await query.answer(messages.action_cannot_be_performed[lang], show_alert=True)
    await query.message.delete()


async def pay_order(user_id: int, order: OrderItem):
    user_balance = await users.get_balance(user_id)
    meta = {
        'internal_order_id': order.internal_order_id,
        'payment_method': PaymentMethod.FROM_BALANCE.value,
    }
    transaction_item = TransactionItem(
        user_id=user_id,
        transaction_type=TransactionType.PAYMENT,
        amount=-abs(order.total_amount),
        balance_after=round((user_balance - order.total_amount), 2),
        meta=meta
    )
    await transactions.save(transaction_item)
    new_balance = round((user_balance - order.total_amount), 2)
    await users.update_balance(user_id, new_balance)
    order.order_status = OrderStatus.PAID
    await orders_queue.update(order)
