from urllib.parse import quote

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery

import config
from core.db import users
from core.db.main_orders_queue import orders_queue
from core.storage import storage
from loader import dp, bot
from utils.keyboards.admin import orders_page
from utils.navigation import get_admin_menu
from utils.order_presentation import short_html


@dp.message(Command('admin'))
async def show_admin_menu(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    if user_id != config.ADMIN_ID:
        return

    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    await storage.delete_data(key)
    await get_admin_menu(user_id)


@dp.message(Command('update_usernames'))
async def users_cmd(msg: types.Message):
    user_id = msg.from_user.id
    if user_id != config.ADMIN_ID:
        return

    user_ids = await users.get_all_users_ids()
    count = 0
    for current_user_id in user_ids:
        try:
            user = await bot.get_chat(current_user_id)
            await users.update_user(current_user_id, {
                'username': user.username if user.username else None,
                'name': user.full_name if user.full_name else None,
            })
            count += 1
        except Exception as error:
            await bot.send_message(config.ADMIN_ID, f'Error updating username for user {current_user_id}: {error}')

    await bot.send_message(config.ADMIN_ID, f'updated {count} from {len(user_ids)} users')


ORDER_PAGE_SIZE = 5


async def _orders_page_text(requested_page: int):
    orders, total = await orders_queue.get_page(requested_page, ORDER_PAGE_SIZE)
    total_pages = max(1, (total + ORDER_PAGE_SIZE - 1) // ORDER_PAGE_SIZE)
    page = min(max(requested_page, 1), total_pages)
    if page != requested_page:
        orders, total = await orders_queue.get_page(page, ORDER_PAGE_SIZE)

    if not orders:
        return 'Пока что нет заказов.', None

    lines = [f'<b>Заказы: страница {page}/{total_pages}</b>', f'Всего заказов: <b>{total}</b>']
    for order in orders:
        username = await users.get_username(order.user_id)
        username_text = f'@{short_html(username.lstrip("@"))}' if username else 'username не указан'
        internal_order_id = short_html(order.internal_order_id)
        deep_link = f'{config.BOT_URL.rstrip("/")}?start=order_{quote(order.internal_order_id, safe="_")}'
        lines.extend((
            '',
            f'🆔 <b>Внутренний ID:</b> <a href="{short_html(deep_link, max_length=128)}">{internal_order_id}</a> · 📅 <code>{short_html(order.creation_date)}</code>',
            f'🔗 <b>Backend ID:</b> <code>{short_html(order.backend_order_id)}</code>',
            f'📊 <b>Статус:</b> <code>{short_html(order.order_status.value)}</code>',
            f'📦 <b>Тип:</b> <code>{short_html(order.service_type.value)}</code>',
            f'💰 <b>Сумма:</b> <code>{order.total_amount:.2f} RUB</code>',
            f'👤 <b>Пользователь:</b> {username_text} (<code>{short_html(order.user_id)}</code>)',
        ))
    keyboard = orders_page(page, total_pages).as_markup() if total_pages > 1 else None
    return '\n'.join(lines), keyboard


@dp.callback_query(F.data == 'manage_orders')
async def show_orders(query: CallbackQuery):
    if query.from_user.id != config.ADMIN_ID:
        await query.answer()
        return
    text, keyboard = await _orders_page_text(1)
    await query.message.answer(text, reply_markup=keyboard)
    await query.answer()


@dp.callback_query(F.data.startswith('admin_orders_page:'))
async def show_orders_page(query: CallbackQuery):
    if query.from_user.id != config.ADMIN_ID:
        await query.answer()
        return
    raw_page = query.data.rsplit(':', 1)[-1]
    if not raw_page.isdigit():
        await query.answer()
        return
    text, keyboard = await _orders_page_text(int(raw_page))
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()