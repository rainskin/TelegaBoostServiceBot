from aiogram import types, F

from loader import dp
from core.db import users, orders
from utils import navigation
from utils.keyboards import navigation_kb, categories
from core.localisation.texts import messages
from utils.api import get_orders_status
from utils.order_status import get_order_status_text


@dp.callback_query(F.data.startswith('current_orders'))
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)

    current_orders_ids = [int(i) for i in orders.get_current_orders(user_id).keys()]
    if current_orders_ids:
        current_orders = await get_orders_status(current_orders_ids, user_id)

        orders_status: str = get_order_status_text(lang, current_orders)

        msg_text = f'<b>{messages.active_orders[lang]}:</b>\n\n{orders_status}'
        orders.move_completed_orders_to_archive(user_id, current_orders)
    else:
        msg_text = messages.no_active_orders[lang]

    await query.message.answer(msg_text, reply_markup=navigation_kb.orders(lang).as_markup())
    await query.answer()
    await query.message.delete()


@dp.callback_query(F.data == 'new_order')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    await navigation.get_categories(user_id)
    await query.answer()
    await query.message.delete()


@dp.callback_query(F.data == 'change_language')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    await query.message.answer(messages.change_lang[lang], reply_markup=navigation_kb.select_lang().as_markup())
    await query.answer()
    await query.message.delete()



