from aiogram import types, F
from aiogram.enums import ContentType
from aiogram.fsm.storage.base import StorageKey

from busines_logic.calculate_commission import get_amount_minus_commission
from core.db import users, admin
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import states
from utils.keyboards.navigation_kb import yes_or_no_kb


@dp.message(F.content_type == ContentType.TEXT, states.BalanceRecharge.choosing_amount)
async def _(msg: types.Message):
    user_id = msg.from_user.id
    lang = users.get_user_lang(user_id)
    chat_id = msg.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    text = msg.text
    data = await storage.get_data(key)

    try:
        value = float(text)
    except ValueError as e:
        await msg.answer(messages.balance_recharge_wrong_amount[lang])
        return

    currency = 'RUB'

    recharge_commission = admin.get_balance_recharge_commission()
    if recharge_commission:
        amount_with_commission = await get_amount_minus_commission(value, recharge_commission)

        formatted_value = f"{amount_with_commission:.2f}"
        text = messages.balance_recharge_accept_amount_with_commission[lang].format(
            commission_amount=recharge_commission, amount=formatted_value, currency=currency)
    else:
        formatted_value = f"{value:.2f}"
        text = messages.balance_recharge_accept_amount[lang].format(amount=formatted_value, currency=currency)
        amount_with_commission = value

    service_msg = await msg.answer(text, reply_markup=yes_or_no_kb(lang).as_markup())

    msgs_to_delete = data.get('msgs_to_delete', [])
    msgs_to_delete += [msg.message_id, service_msg.message_id]
    await storage.update_data(key, amount=value, amount_with_commission=amount_with_commission, msgs_to_delete=msgs_to_delete)



