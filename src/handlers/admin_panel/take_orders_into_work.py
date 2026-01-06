from aiogram import F
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery

from busines_logic.order_managment.take_into_work import take_orders_into_work
from core.db import users, admin
from core.storage import storage
from loader import dp, bot
from utils import states, api
from utils.keyboards import navigation_kb


@dp.callback_query(F.data == 'to_take_all_orders', states.AdminStates.to_take_orders_into_work)
async def _(query: CallbackQuery):
    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    data = await storage.get_data(key)
    lang = await users.get_user_lang(user_id)
    total_orders = data.get('total_orders')
    total_amount: float = data.get('total_amount')

    current_balance = await api.get_account_balance()
    if current_balance > total_amount:
        text = (f'<b>Текущий баланс:</b> {current_balance} руб.\n'
                f'Оформить <b>{total_orders}</b> заказ(ов)? Будет списано: <b>{total_amount:.2f} руб.</b>')
        kb = navigation_kb.yes_or_no_kb(lang).as_markup()
    else:
        text = (f'<b>Недостаточно средств.</b>\n'
                f'Текущий баланс: <b>{current_balance:.2f} руб.</b>\n'
                f'Необходимо пополнить счет еще минимум на <b>{round((total_amount - current_balance), 2)} руб.</b>')
        kb = None

    await query.message.answer(text, reply_markup=kb)
    await query.message.delete()
    await query.answer()


@dp.callback_query(F.data == 'yes', states.AdminStates.to_take_orders_into_work)
async def _(query: CallbackQuery):
    await query.message.answer('Начинаю оформление заказов')
    await query.answer()
    await query.message.delete()

    _orders = await admin.get_orders_for_execution()

    await take_orders_into_work(_orders)


@dp.callback_query(F.data == 'no', states.AdminStates.to_take_orders_into_work)
async def _(query: CallbackQuery):
    await query.message.answer('Действие отменено')
    await query.message.delete()
    await query.answer()
