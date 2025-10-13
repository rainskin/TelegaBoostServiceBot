from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

import config
from core.db import users, admin
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
    # data = await storage.get_data(key)

    currency = 'RUB'
    minimal_recharge_amount = admin.get_minimal_recharge_amount()

    text = messages.balance_recharge_limits[lang]
    topup_commission = admin.get_balance_recharge_commission()
    if topup_commission > 0:
        text += f'\n\n{messages.balance_recharge_commission_info[lang].format(topup_commission=topup_commission, support_contact=config.SUPPORT_BOT_URL)}'
    limits_msg = await query.message.answer(text)
    service_msg = await query.message.answer(messages.balance_recharge_input_amount[lang].format(
            minimal_recharge_amount=minimal_recharge_amount, currency=currency))

    await query.answer()
    await state.set_state(states.BalanceRecharge.choosing_amount)

    # msgs_to_delete = data.get('msgs_to_delete', [])
    msgs_to_delete = [limits_msg.message_id, service_msg.message_id]

    await storage.set_data(key, msgs_to_delete=msgs_to_delete, minimal_recharge_amount=minimal_recharge_amount, currency=currency)
