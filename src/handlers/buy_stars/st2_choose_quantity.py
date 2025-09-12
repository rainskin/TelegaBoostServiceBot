from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import states


@dp.message(states.BuyStars.waiting_for_amount)
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.chat.id
    key = StorageKey(bot.id, user_id, user_id)
    data = await storage.get_data(key)
    msgs_to_delete = data.get('msgs_to_delete', [])
    await storage.update_data(key, msgs_to_delete=msgs_to_delete + [msg.message_id])
    lang = users.get_user_lang(user_id)
    try:
        quantity = int(msg.text)
    except ValueError:
        wrong_amount_msg = await msg.answer(messages.tg_stars_wrong_amount[lang])
        await storage.update_data(key, msgs_to_delete=msgs_to_delete + [wrong_amount_msg.message_id])
        return
    if not is_correct_amount(quantity):
        not_correct_amount_message = await msg.answer(messages.tg_stars_not_correct_amount[lang])
        await storage.update_data(key, msgs_to_delete=msgs_to_delete + [not_correct_amount_message.message_id])
        return

    confirmation_text = messages.tg_stars_enter_username[lang].format(quantity=quantity)

    confirmation_message = await msg.answer(confirmation_text)
    await storage.update_data(key, quantity=quantity, msgs_to_delete=msgs_to_delete + [confirmation_message.message_id])
    await state.set_state(states.BuyStars.waiting_for_username)


def is_correct_amount(amount: int) -> bool:
    return 50 <= amount <= 1000000
