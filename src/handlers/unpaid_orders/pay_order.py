from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message

from core.db.main_orders_que import orders_queue
from core.localisation.texts import messages
from core.storage import storage
from enums.orders.order_status import OrderStatus
from loader import dp, bot
from core.db import users
from utils import callback_templates
from busines_logic import special_offers
from utils.keyboards import categories, payment_methods
from utils.category_names import get_category_name
from utils.keyboards.navigation_kb import navigation
from utils.states import Payment

"""
Обработка нажатия кнопки "Оплатить заказ" под неоплаченным заказом.
"""

callback_template = callback_templates.pay_unpaid_order_template()


@dp.callback_query(F.data.startswith(callback_template))
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    key = StorageKey(bot.id, user_id, user_id)
    lang = users.get_user_lang(user_id)

    internal_order_id = query.data.replace(callback_template, '')
    order_status = orders_queue.get_status(internal_order_id)

    await query.answer()

    if order_status == OrderStatus.UNPAID:
        await send_payment_keyboard(user_id, internal_order_id, state)
        await storage.update_data(key, internal_order_id=internal_order_id, message_with_order_info_id=query.message.message_id)
        await state.set_state(Payment.choosing_method)

    else:
        text = messages.unpaid_order_failed_to_do[lang].format(internal_order_id=internal_order_id, status=order_status.value)
        await query.message.edit_text(text, reply_markup=None)


async def send_payment_keyboard(user_id: int, internal_order_id: str, state: FSMContext):
    lang = users.get_user_lang(user_id)
    order_item = orders_queue.get(internal_order_id)
    currency = 'RUB'
    user_balance = users.get_balance(user_id)

    kb = payment_methods.kb(lang, from_balance=True)
    text = messages.confirm_order_payment[lang].format(total_amount=order_item.total_amount,
                                                       currency=currency, current_balance=user_balance)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb.as_markup())


