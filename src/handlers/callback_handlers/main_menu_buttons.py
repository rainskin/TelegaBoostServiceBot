

from aiogram import types, F
from aiogram.fsm.storage.base import StorageKey

from core.storage import storage
from handlers.callback_handlers.orders_navigation_buttons import  get_order_statuses_text
from loader import dp, bot
from core.db import users, orders
from utils import navigation
from utils.keyboards import navigation_kb
from core.localisation.texts import messages
from utils.keyboards.navigation_kb import cancel_order


@dp.callback_query(F.data == 'current_orders')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    await storage.set_data(key, current_orders=True)
    not_accepted_orders = orders.get_not_accepted_orders(user_id)
    if not_accepted_orders:
        await query.message.answer(messages.not_accepted_order[lang])
        for _order_id, _order_info in not_accepted_orders.items():
            url = _order_info.get('url')
            quantity = _order_info.get('quantity')
            total_amount = _order_info.get('total_amount')

            text = messages.not_accepted_order_status[lang].format(order_id=_order_id, url=url, quantity=quantity, total_amount=total_amount)
            kb = cancel_order(lang, _order_id)
            await query.message.answer(text, reply_markup=kb.as_markup())

    await get_order_statuses_text(user_id, lang, current_orders=True)
    await query.answer()


@dp.callback_query(F.data == 'archive_orders')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    await storage.set_data(key, current_orders=False)

    await get_order_statuses_text(user_id, lang)
    await query.answer()


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

