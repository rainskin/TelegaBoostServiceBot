from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery

import config
from busines_logic.order_managment.take_into_work import try_get_orders_for_execution, get_summary_text, \
    get_total_amount
from core.db import admin, users
from core.storage import storage
from loader import dp, bot
from utils import states, api
from utils.keyboards.admin import orders_manage
from utils.navigation import  get_admin_menu


@dp.message(Command('admin'))
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    if user_id != config.ADMIN_ID:
        return

    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    await storage.delete_data(key)
    await get_admin_menu(user_id)

# @dp.message(Command('refund'))
# async def refund(msg: types.Message):
#     user_id = msg.from_user.id
#     if user_id != config.ADMIN_ID:
#         return
#     await bot.refund_star_payment(msg.from_user.id, refund_id)
#
#


@dp.message(Command('update_usernames'))
async def users_cmd(msg: types.Message):
    user_id = msg.from_user.id
    if user_id != config.ADMIN_ID:
        return

    user_ids = users.get_all_users_ids()

    count = 0
    for user_id in user_ids:
        try:
            user = await bot.get_chat(user_id)
            username = user.username if user.username else None
            name = user.full_name if user.full_name else None

            doc = {'username': username,
                   'name': name}
            
            users.update_user(user_id, doc)
            count += 1
        except Exception as e:
            await bot.send_message(config.ADMIN_ID, f"Error updating username for user {user_id}: {e}")

    await bot.send_message(config.ADMIN_ID, f'updated {count} from {len(user_ids)} users')



@dp.callback_query(F.data == 'manage_orders')
async def _ (query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)

    orders = try_get_orders_for_execution()
    available_balance = await api.get_account_balance()
    if orders:
        total_amount = get_total_amount(orders)
        text = get_summary_text(orders, available_balance)
        kb = orders_manage().as_markup()
        await storage.set_data(key, total_orders=len(orders), total_amount=total_amount)

    else:
        text = 'Пока что нет заказов'
        kb = None

    await query.message.answer(text, reply_markup=kb)
    await state.set_state(states.AdminStates.to_take_orders_into_work)
    await query.answer()
