from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users, orders, admin
from core.db.main_orders_queue import orders_queue
from core.db.models.transaction_item import TransactionItem
from core.db.transactions import transactions
from core.localisation.texts import messages
from core.storage import storage
from enums.orders.order_status import OrderStatus
from enums.transaction_type import TransactionType
from loader import dp, bot
from utils import callback_templates
from utils.keyboards import navigation_kb
from utils.states import ManageOrders

template = callback_templates.cancel_order()


@dp.callback_query(F.data.startswith(template))
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    internal_order_id: str = query.data.replace(template, '')
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    status = orders_queue.get_status(internal_order_id)
    if is_not_accepted_order(user_id, internal_order_id) and status != OrderStatus.IN_PROGRESS:
        if not orders.is_order_exist(user_id, internal_order_id,
                                     not_accepted_order=True) or admin.is_order_in_execution_queue(internal_order_id):
            text = messages.canceling_not_accepted_order_is_not_available[lang]
            kb = None
        else:
            text = messages.cancel_order[lang].format(order_id=internal_order_id)
            kb = navigation_kb.yes_or_no_kb(lang).as_markup()
    else:
        text = messages.action_is_not_available[lang]
        kb = None

    await query.message.edit_text(text, reply_markup=kb)
    await storage.set_data(key, order_id=internal_order_id)
    await state.set_state(ManageOrders.cancel_order)
    await query.answer()


@dp.callback_query(F.data == 'yes', ManageOrders.cancel_order)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    lang = users.get_user_lang(user_id)
    data = await storage.get_data(key)
    internal_order_id = data.get('order_id')

    if is_not_accepted_order(user_id, internal_order_id):
        not_accepted_orders = orders.get_not_accepted_orders(user_id)
        order = not_accepted_orders.get(internal_order_id)
        amount = order.get('total_amount')
        user_balance = users.get_balance(user_id)

        transaction_item = TransactionItem(
            user_id=user_id,
            transaction_type=TransactionType.REVERSAL,
            amount=amount,
            balance_after=round((user_balance + amount), 2),
        )
        await transactions.save(transaction_item)

        orders.cancel_order(user_id, internal_order_id, not_accepted_orders=True)

        try:
            order_item = orders_queue.get(internal_order_id)
            order_item.order_status = OrderStatus.CANCELED
            orders_queue.update(order_item)
        except Exception:
            pass

        admin.remove_order_from_main_queue(internal_order_id)

    await query.message.edit_text(messages.order_successfully_canceled[lang])

    await storage.delete_data(key)
    await state.set_state(None)
    await query.answer()


@dp.callback_query(F.data == 'no', ManageOrders.cancel_order)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    lang = users.get_user_lang(user_id)
    await query.message.answer(messages.cancel_action[lang])

    await storage.delete_data(key)
    await query.message.delete()
    await state.set_state(None)
    await query.answer()


def is_not_accepted_order(user_id: int, order_id: str):
    return order_id.startswith(str(user_id))
