from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery

import config
from core.db import admin, users
from core.storage import storage
from loader import dp, bot
from utils import  states
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

    orders_to_execution = admin.get_orders_for_execution()
    if orders_to_execution:
        orders = orders_to_execution
    else:
        orders_queue: dict = admin.get_orders_queue()
        orders = orders_queue

    if orders:
        total_orders: int = 0
        total_amount: float = 0
        previously_paid = 0
        total_spent_by_users = 0
        total_profit = 0
        for order_id, order_info in orders.items():
            total_amount += order_info['amount_without_commission']
            total_spent_by_users += order_info['total_amount']
            total_profit += order_info['profit']
            total_orders += 1

        text = (f'<b>Текущая очередь заказов</b>\n\n'
                f'<b>Всего заказов:</b> {total_orders}\n'
                f'<b>Для оплаты необходимо:</b> {round(total_amount, 2)}\n'
                f'<b>Потрачено пользователями:</b> {total_spent_by_users:.2f}\n'
                f'<b>Прибыль:</b> {round(total_profit, 2)}')
        kb = orders_manage().as_markup()
        await storage.set_data(key, total_orders=total_orders, total_amount=total_amount)
    else:
        text = 'Пока что нет заказов'
        kb = None
    await query.message.answer(text, reply_markup=kb)
    await state.set_state(states.AdminStates.to_take_orders_into_work)
    await query.answer()
