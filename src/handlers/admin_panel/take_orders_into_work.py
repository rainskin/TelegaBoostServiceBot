from aiogram import F
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery

from core.db import users, admin, orders
from core.localisation.texts import messages
from core.storage import storage
from handlers.new_order.create import create_order
from loader import dp, bot
from utils import states, api
from utils.keyboards import navigation_kb


@dp.callback_query(F.data == 'to_take_all_orders', states.AdminStates.to_take_orders_into_work)
async def _(query: CallbackQuery):
    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    data = await storage.get_data(key)
    lang = users.get_user_lang(user_id)
    total_orders = data.get('total_orders')
    total_amount = data.get('total_amount')

    current_balance = await api.get_account_balance()
    if current_balance > total_amount:
        text = (f'<b>Текущий баланс:</b> {current_balance} руб.\n'
                f'Оформить <b>{total_orders}</b> заказ(ов)? Будет списано: <b>{total_amount} руб.</b>')
        kb = navigation_kb.yes_or_no_kb(lang).as_markup()
    else:
        text = (f'<b>Недостаточно средств.</b>\n'
                f'Текущий баланс: <b>{current_balance} руб.</b>\n'
                f'Необходимо пополнить счет еще минимум на <b>{round((total_amount - current_balance), 2)} руб.</b>')
        kb = None

    await query.message.answer(text, reply_markup=kb)
    await query.message.delete()
    await query.answer()


async def send_notification_to_user(user_id, order_id):
    lang = users.get_user_lang(user_id)
    text = messages.take_order_into_work[lang].format(order_id=order_id)
    await bot.send_message(user_id, text)


@dp.callback_query(F.data == 'yes', states.AdminStates.to_take_orders_into_work)
async def _(query: CallbackQuery):
    _orders = admin.get_orders_for_execution()

    msg = await query.message.answer('Начинаю оформление заказов')
    await query.answer()
    await query.message.delete()

    count = 0
    for internal_order_id, order_info in _orders.items():
        user_id = order_info.get('user_id')

        order_id = await create_order(internal_order_id, order_info)

        admin.remove_order_from_execution_queue(internal_order_id)
        orders.remove_not_accepted_order(user_id, internal_order_id)

        await send_notification_to_user(user_id, order_id)  # TODO: handle error if user block bot 
        count += 1
        await bot.edit_message_text(f'Оформил {count} заказ(ов)', query.from_user.id, msg.message_id)

    await bot.send_message(query.from_user.id, 'Закончил оформление заказов', )


@dp.callback_query(F.data == 'no', states.AdminStates.to_take_orders_into_work)
async def _(query: CallbackQuery):
    await query.message.answer('Действие отменено')
    await query.message.delete()
    await query.answer()

