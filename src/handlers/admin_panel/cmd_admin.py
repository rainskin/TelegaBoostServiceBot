from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery

import config
from core.db import admin
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
        total_orders = 0
        total_amount = 0
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
                f'<b>Для оплаты необходимо:</b> {total_amount}\n'
                f'<b>Потрачено пользователями:</b> {total_spent_by_users}\n'
                f'<b>Прибыль:</b> {round(total_profit, 2)}')
        kb = orders_manage().as_markup()
        await storage.set_data(key, total_orders=total_orders, total_amount=total_amount)
    else:
        text = 'Пока что нет заказов'
        kb = None
    await query.message.answer(text, reply_markup=kb)
    await state.set_state(states.AdminStates.to_take_orders_into_work)
    await query.answer()
