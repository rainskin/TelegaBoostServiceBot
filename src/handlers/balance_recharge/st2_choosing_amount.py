from aiogram import types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import states
from utils.keyboards.navigation_kb import yes_or_no_kb


@dp.message(F.content_type == ContentType.TEXT, states.BalanceRecharge.choosing_amount)
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    lang = users.get_user_lang(user_id)
    chat_id = msg.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    text = msg.text
    print(text)

    try:
        value = float(text)
        print(value)
    except ValueError as e:
        await msg.answer(messages.balance_recharge_wrong_amount[lang])
        return

    value = round(value, 2)
    currency = 'RUB'
    await msg.answer(messages.balance_recharge_accept_amount[lang].format(amount=value, currency=currency),
                     reply_markup=yes_or_no_kb(lang).as_markup())
    await storage.set_data(key, amount=value)
