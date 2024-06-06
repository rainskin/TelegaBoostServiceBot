from typing import List

import aiogram
from aiogram import types, F
from aiogram.fsm.storage.base import StorageKey

from core.storage import storage
from handlers.callback_handlers.orders_navigation_buttons import get_unshown_orders, get_order_statuses_text
from loader import dp, bot
from core.db import users, orders
from utils import navigation
from utils.keyboards import navigation_kb, categories
from core.localisation.texts import messages
from utils.api import get_order_statuses
from utils.order_status import get_order_status_text


@dp.callback_query(F.data == 'current_orders')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    await storage.set_data(key, current_orders=True)
    await get_order_statuses_text(user_id, lang, current_orders=True)
    await query.answer()
    await query.message.delete()


@dp.callback_query(F.data == 'archive_orders')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    await storage.set_data(key, current_orders=False)

    await get_order_statuses_text(user_id, lang)
    await query.answer()
    await query.message.delete()


@dp.callback_query(F.data == 'new_order')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    await storage.delete_data(key)
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

