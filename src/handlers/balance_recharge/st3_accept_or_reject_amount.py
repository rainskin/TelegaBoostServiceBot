from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users, admin
from core.localisation.texts import messages
from core.storage import storage
from handlers.new_order.st4_make_order import get_internal_order_id
from loader import dp, bot
from utils import states, navigation
from utils.Payment_methods.aaio.methods import get_payment_url
from utils.keyboards.payment_methods import card_payment


async def get_payment_info(user_id: int, amount: float, payment_url: str, balance_recharge=False, payment_status=None):
    payment_purpose = 'balance_recharge' if balance_recharge else None
    return {
        'user_id': user_id,
        'amount': amount,
        'payment_url': payment_url,
        'payment_purpose': payment_purpose,
        'status': payment_status,
    }


@dp.callback_query(F.data == 'yes', states.BalanceRecharge.choosing_amount)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id

    key = StorageKey(bot.id, user_id, user_id)
    lang = users.get_user_lang(user_id)

    data = await storage.get_data(key)
    amount = data.get('amount')

    internal_order_id = await get_internal_order_id(user_id)
    payment_id = f'P{internal_order_id}'
    text = messages.payment_by_card[lang].format(order_id=payment_id)
    payment_url = await get_payment_url(payment_id, amount, lang)
    payment_info = await get_payment_info(user_id, amount, payment_url, balance_recharge=True)

    admin.save_payment(payment_id, payment_info)

    kb = card_payment(lang, payment_url, payment_id, balance_recharge=True)
    await query.message.answer(text, reply_markup=kb.as_markup())
    await query.answer()
    await query.message.delete()
    await state.set_state(states.BalanceRecharge.choosing_amount)


@dp.callback_query(F.data == 'no', states.BalanceRecharge.choosing_amount)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    text = messages.cancel_action[lang]

    await query.message.answer(text)
    await state.set_state(None)
    await navigation.return_to_menu(user_id, state)
    await query.message.delete()
