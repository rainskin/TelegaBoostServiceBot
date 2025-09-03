import re

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.storage import storage
from loader import dp, bot
from utils import states
from utils.keyboards.navigation_kb import yes_or_no_kb


@dp.message(states.BuyStars.waiting_for_username)
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.chat.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot.id, user_id, user_id)
    data = await storage.get_data(key)
    quantity = data.get('quantity')
    msgs_to_delete = data.get('msgs_to_delete', [])

    await storage.update_data(key, msgs_to_delete=msgs_to_delete + [msg.message_id])
    recipient_username = msg.text.strip()

    if recipient_username.startswith('@'):
        recipient_username = recipient_username[1:]

    if not is_valid_username(recipient_username):
        error_message_text = "Invalid username. Please enter a valid username (5-32 characters, letters, numbers, and underscores only)."
        error_message = await msg.answer(error_message_text)
        msgs_to_delete.append(error_message.message_id)
        await storage.update_data(key, msgs_to_delete=msgs_to_delete + [error_message.message_id])
        return

    amount_without_commission = quantity
    total_amount = calculate_price(quantity)
    confirmation_text = (f"You have selected to buy {quantity} stars for @{recipient_username}.\n"
                         f"\nThe total price is {total_amount} RUB. "
                         f"Click Yes to confirm or No to cancel.")
    kb = yes_or_no_kb(lang).as_markup()
    confirmation_message = await msg.answer(confirmation_text, reply_markup=kb)

    await state.set_state(states.BuyStars.confirmation)
    await storage.update_data(key, recipient=recipient_username, amount_without_commission=amount_without_commission, total_amount=total_amount, msgs_to_delete=msgs_to_delete + [confirmation_message.message_id])
    # already in storage: amount, msgs_to_delete


def is_valid_username(username: str) -> bool:
    pattern = r'^[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, username))


def calculate_price(amount: int) -> int:
    coefficient = 1.5
    return int(amount * coefficient)
