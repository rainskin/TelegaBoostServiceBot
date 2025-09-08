import re

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from busines_logic.process_orders.tg_stars_order import calculate_price_rub
from core.db import users
from core.storage import storage
from loader import dp, bot
from utils import states
from utils.currencies import usdt
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

    usdt_to_rub_rate = usdt.to_rub_rate()
    total_amount = calculate_price_rub(quantity)
    profit = round(calculate_profit(quantity, total_amount, usdt_to_rub_rate), 2)
    amount_without_commission = total_amount - profit
    confirmation_text = (f"You have selected to buy {quantity} stars for @{recipient_username}.\n"
                         f"\nThe total price is {total_amount} RUB. "
                         f"Click Yes to confirm or No to cancel.")
    kb = yes_or_no_kb(lang).as_markup()
    confirmation_message = await msg.answer(confirmation_text, reply_markup=kb)

    await state.set_state(states.BuyStars.confirmation)
    await storage.update_data(key, recipient=recipient_username, amount_without_commission=amount_without_commission, total_amount=total_amount, profit=profit, msgs_to_delete=msgs_to_delete + [confirmation_message.message_id])
    # already in storage: amount, msgs_to_delete


def is_valid_username(username: str) -> bool:
    pattern = r'^[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, username))


def calculate_profit(stars: int, total_price: float, usd_rub_rate: float, payment_fee: float = 0.16) -> float:
    """
    Считает себестоимость, выручку и профит с учётом комиссии платёжки.

    :param stars: количество звёзд
    :param total_price: итоговая цена для клиента в рублях
    :param usd_rub_rate: курс доллара к рублю
    :param payment_fee: комиссия платёжки (0.16 = 16%)
    """

    # Себестоимость (в рублях) = 0.015 $ * курс
    cost_per_star = 0.015 * usd_rub_rate
    total_cost = stars * cost_per_star

    # Чистая выручка после комиссии
    net_revenue = total_price * (1 - payment_fee)

    # Профит
    profit = net_revenue - total_cost

    return profit

