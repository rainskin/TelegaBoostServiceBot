from aiogram import F, types
from aiogram.fsm.context import FSMContext

from core.db import users
from core.localisation.texts import messages
from loader import dp
from utils import states
from utils.keyboards import payment_methods


@dp.callback_query(F.data == 'yes', states.BalanceRecharge.choosing_amount)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)

    text = messages.available_payment_methods[lang].format()

    kb = payment_methods.kb(lang, from_card=True, from_telegram_stars=True).as_markup()
    await query.message.answer(text, reply_markup=kb)
    await query.answer()
    await query.message.delete()
    await state.set_state(states.Payment.choosing_method)

