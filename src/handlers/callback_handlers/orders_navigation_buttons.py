from typing import List

import aiogram
from aiogram import types, F
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import InlineKeyboardButton

from core.storage import storage
from loader import dp, bot
from core.db import users, orders
from utils import navigation
from utils.keyboards import navigation_kb, categories
from core.localisation.texts import messages
from utils.api import get_order_statuses
from utils.order_status import get_order_status_text

# previous_btn = builder.button(text='<<', callback_data='previous_page')
#     number_btn = builder.button(text=f'{current_page}/{amount_pages}', callback_data='number_button')
#     next_btn = builder.button(text='>>', callback_data='next_page')

@dp.callback_query(F.data == 'previous_page')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    lang = users.get_user_lang(user_id)

    data = await storage.get_data(key)
    current_orders = data['current_orders']

    keyboards = query.message.reply_markup.inline_keyboard
    current_page = get_current_page_number_from_inline_keyboards_info(keyboards)

    page = current_page - 1

    await get_order_statuses_text(user_id, lang, current_orders=current_orders, current_page=page)
    await query.answer()
    await query.message.delete()

@dp.callback_query(F.data == 'next_page')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    lang = users.get_user_lang(user_id)

    data = await storage.get_data(key)
    current_orders = data['current_orders']

    keyboards = query.message.reply_markup.inline_keyboard
    current_page = get_current_page_number_from_inline_keyboards_info(keyboards)

    page = current_page + 1

    await get_order_statuses_text(user_id, lang, current_orders=current_orders, current_page=page)
    await query.answer()
    await query.message.delete()


def get_current_page_number_from_inline_keyboards_info(keyboards: list[list[InlineKeyboardButton]]):
    navigation_buttons = keyboards[0]
    current_page = 1
    for button in navigation_buttons:
        if button.callback_data != 'number_button':
            continue

        text = button.text
        current_page = text[0]

    return int(current_page)
def get_unshown_orders(order_ids: list, current_page, orders_per_page: int):
    number_of_orders = len(order_ids)

    if current_page != 1:
        shown_orders = (current_page - 1) * orders_per_page
    else:
        shown_orders = 0

    if shown_orders > number_of_orders:
        shown_orders = number_of_orders

    unshown_orders = number_of_orders - shown_orders

    if unshown_orders < orders_per_page:
        unshown_orders = shown_orders + unshown_orders
    else:
        unshown_orders = shown_orders + orders_per_page

    return order_ids[shown_orders:unshown_orders]


async def get_order_statuses_text(user_id: int, lang: str, current_orders=False, current_page=1):
    if current_orders:
        _orders = orders.get_current_orders(user_id)
    else:
        _orders = orders.get_orders_from_archive(user_id)

    order_ids = [i for i in _orders.keys()]

    if order_ids:
        if current_orders:
            msg_text = f'<b>{messages.active_orders[lang]}:</b>'
        else:
            msg_text = f'<b>{messages.history_of_orders[lang]}:</b>'

        orders_per_page = 2
        number_of_orders = len(order_ids)
        amount_pages = (number_of_orders + orders_per_page - 1) // orders_per_page
        _order_ids = get_unshown_orders(order_ids, current_page, orders_per_page)

        current_order_statuses = await get_order_statuses(_order_ids, user_id)
        orders_statuses: str = get_order_status_text(user_id, lang, current_order_statuses, current_orders)
        msg_text = f'{msg_text}\n\n{orders_statuses}'

        msg = await bot.send_message(user_id, msg_text,
                                     reply_markup=navigation_kb.orders(lang, current_page, amount_pages,
                                                                       current_orders).as_markup())

    else:
        if current_orders:
            msg_text = messages.no_active_orders[lang]
        else:
            msg_text = messages.no_history_of_orders[lang]

        await bot.send_message(msg_text)
