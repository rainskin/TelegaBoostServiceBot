from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

import config
from core.db import users
from core.localisation.texts import messages
from core.localisation.texts.buttons import buy_stars_button
from core.storage import storage
from loader import bot, dp
from utils import states
from utils.callback_templates import balance_recharge_template




@dp.callback_query(F.data == buy_stars_button.get('callback'))
async def handle_payment(query: types.CallbackQuery, state: FSMContext):
    # user_id = query.from_user.id
    # if user_id != config.ADMIN_ID:
    #     await query.answer('Will available soon')
    #     return
    await cmd_handler(query.message, state)
    await query.answer()
    await query.message.delete()



@dp.message(Command('buy_stars'))
async def cmd_handler(msg: types.Message, state: FSMContext):
    user_id = msg.chat.id
    # if user_id != config.ADMIN_ID:
    #     return

    key = StorageKey(bot.id, user_id, user_id)
    data = await storage.get_data(key)
    msgs_to_delete = data.get('msgs_to_delete', [])

    lang = await users.get_user_lang(user_id)

    await state.set_state(None)
    answer = await msg.answer(messages.tg_stars_enter_quantity[lang])
    await storage.update_data(key, msgs_to_delete=msgs_to_delete + [answer.message_id])
    await state.set_state(states.BuyStars.waiting_for_amount)
