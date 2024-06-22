from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import states


@dp.callback_query(F.data == 'balance_recharge')
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot.id, user_id, user_id)

    await storage.delete_data(key)
    await query.message.answer(messages.balance_recharge_limits[lang])
    await query.message.answer(messages.balance_recharge_input_amount[lang])
    await query.answer()
    await state.set_state(states.BalanceRecharge.choosing_amount)
