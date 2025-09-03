from aiogram import types, F

from core.db.main_orders_que import orders_queue
from core.localisation.texts import messages
from enums.orders.order_status import OrderStatus
from loader import dp
from core.db import users
from utils import callback_templates
from busines_logic import special_offers
from utils.keyboards import categories
from utils.category_names import get_category_name
from utils.keyboards.navigation_kb import navigation

"""
Обработка нажатия кнопки "Удалить" под неоплаченным заказом.
"""

callback_template = callback_templates.delete_unpaid_order_template()


@dp.callback_query(F.data.startswith(callback_template))
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    internal_order_id = query.data.replace(callback_template, '')

    order_status = OrderStatus(orders_queue.get_status(internal_order_id))

    if order_status == OrderStatus.UNPAID:

        orders_queue.delete(internal_order_id)

        notification = '!!!УДАЛЕН!!!'
        text = f'Ваш неоплаченный заказ {internal_order_id} был удалён.'
        await query.answer()
        await query.message.edit_text(f'{text}\n\n{notification}', reply_markup=None)

    else:
        text = f'Текущий статус заказа {internal_order_id}: {order_status.value}'
        await query.message.edit_text(text, reply_markup=None)

