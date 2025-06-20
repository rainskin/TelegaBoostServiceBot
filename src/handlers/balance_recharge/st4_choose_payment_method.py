from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import states
from utils.keyboards import payment_methods


@dp.callback_query(F.data == 'yes', states.BalanceRecharge.choosing_amount)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot.id, user_id, user_id)
    data = await storage.get_data(key)
    msgs_to_delete = data.get('msgs_to_delete', [])
    text = messages.available_payment_methods[lang].format()

    kb = payment_methods.kb(lang, from_card=True, from_telegram_stars=True).as_markup()
    await query.message.answer(text, reply_markup=kb)
    await query.answer()
    await query.message.delete()
    for msg_id in msgs_to_delete:
        try:
            await bot.delete_message(user_id, msg_id)
        except Exception as e:
            print(f"Error deleting message {msg_id}: {e}")
    await state.set_state(states.Payment.choosing_method)

