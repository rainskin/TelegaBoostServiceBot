from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from config import ADMIN_ID
from core.db import users
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils.keyboards import payment_methods
from utils.states import NewOrder, Payment

@dp.callback_query(F.data == 'make_order', NewOrder.check_details)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    chat_id = query.message.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    service_msg_ids: list = data['service_msg_ids']

    total_amount = data['total_amount']
    currency = 'RUB'

    await query.answer()

    if service_msg_ids:
        await bot.delete_messages(chat_id, service_msg_ids)
        service_msg_ids = []

    if user_id == ADMIN_ID:
        kb = payment_methods.kb(lang, from_balance=True)
    else:
        kb = payment_methods.kb(lang)

    text = messages.select_payment_method[lang].format(total_amount=total_amount, currency=currency)
    msg = await query.message.answer(text, reply_markup=kb.as_markup())
    await state.set_state(Payment.choosing_method)
    service_msg_ids.append(msg.message_id)
