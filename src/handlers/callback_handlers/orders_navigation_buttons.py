from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import InlineKeyboardButton

from core.db import users, orders
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import states
from utils.api import get_order_statuses
from utils.keyboards import navigation_kb
from utils.order_status import get_order_status_text


@dp.callback_query(F.data == 'previous_page')
async def _(query: types.CallbackQuery, state: FSMContext):
    if await state.get_state() != states.ManageOrders.scroll_orders:
        await query.answer('Меню устарело. Откройте заказы заново.')
        return

    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    lang = users.get_user_lang(user_id)

    data = await storage.get_data(key)
    current_orders = data['current_orders']
    order_ids = data.get('order_ids')

    keyboards = query.message.reply_markup.inline_keyboard
    current_page = get_current_page_number_from_inline_keyboards_info(keyboards)

    page = current_page - 1

    await get_order_statuses_text(user_id, lang, order_ids, current_orders=current_orders, current_page=page)
    await query.answer()
    await query.message.delete()


@dp.callback_query(F.data == 'next_page')
async def _(query: types.CallbackQuery, state: FSMContext):
    if await state.get_state() != states.ManageOrders.scroll_orders:
        await query.answer('Меню устарело. Откройте заказы заново.')
        return

    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    lang = users.get_user_lang(user_id)

    data = await storage.get_data(key)
    current_orders = data['current_orders']
    order_ids = data.get('order_ids')

    keyboards = query.message.reply_markup.inline_keyboard
    current_page = get_current_page_number_from_inline_keyboards_info(keyboards)

    page = current_page + 1

    await get_order_statuses_text(user_id, lang, order_ids, current_orders=current_orders, current_page=page)
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


def get_orders_for_page(order_ids: list, current_page: int, orders_per_page: int):
    """
    Возвращает список заказов, относящихся к текущей странице.
    """
    number_of_orders = len(order_ids)

    start_index = (current_page - 1) * orders_per_page
    end_index = start_index + orders_per_page

    # Гарантируем, что не выйдем за пределы списка
    start_index = min(start_index, number_of_orders)
    end_index = min(end_index, number_of_orders)

    page_orders = order_ids[start_index:end_index]
    return page_orders


async def try_get_orders(user_id: int, lang: str, current_orders: bool = False) -> dict | None:
    # if current_orders - True, then we are getting current orders
    # if current_orders - False, then we are getting archive orders

    # take orders from database

    if current_orders:
        _orders = orders.get_current_orders(user_id)
        no_orders_text = messages.no_active_orders[lang]

    else:
        _orders = orders.get_orders_from_archive(user_id)
        no_orders_text = messages.no_history_of_orders[lang]

    # if there are no orders in database, then we will not send message

    if _orders:
        return _orders

    else:
        await bot.send_message(user_id, no_orders_text,
                               reply_markup=navigation_kb.orders(lang, current_orders).as_markup())
        return None


def get_order_ids(orders: dict):
    order_ids = [i for i in orders.keys()]
    order_ids.reverse()
    return order_ids


async def get_order_statuses_text(user_id: int, lang: str, order_ids: list, current_orders=False, current_page=1):
    if current_orders:
        first_message_text = messages.receiving_information_about_current_orders[lang]
        orders_text = f'<b>{messages.active_orders[lang]}:</b>'

    else:
        first_message_text = messages.receiving_information_about_archive_orders[lang]
        orders_text = f'<b>{messages.history_of_orders[lang]}:</b>'

    message = await bot.send_message(user_id, first_message_text)

    orders_per_page = 5
    number_of_orders = len(order_ids)
    amount_pages = (number_of_orders + orders_per_page - 1) // orders_per_page

    # Which orders have not yet been shown
    _order_ids = get_orders_for_page(order_ids, current_page, orders_per_page)
    current_order_statuses = await get_order_statuses(_order_ids)

    orders_statuses_text: str = get_order_status_text(user_id, lang, current_order_statuses)
    print('orders_statuses:', current_order_statuses)

    # if current_orders:

    orders_text = f'{orders_text}\n\n{orders_statuses_text}'

    await bot.edit_message_text(orders_text, chat_id=user_id, message_id=message.message_id,
                                reply_markup=navigation_kb.orders(lang, current_page, amount_pages,
                                                                  current_orders).as_markup())
