from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from busines_logic.calculate_commission import get_amount_minus_commission
from busines_logic.referrals_managment import add_referral_reward
from core.db import users, orders, admin
from core.db.admin import build_payment_info
from core.db.models.transaction_item import TransactionItem
from core.db.transactions import transactions
from core.localisation.texts import messages
from core.storage import storage
from enums.transaction_type import TransactionType
from handlers.new_order.st4_make_order import get_internal_order_id
from loader import dp, bot
from utils import callback_templates, navigation, states
from utils.payment_methods.SiteAPI import payment_url, payment_status
from utils.keyboards.payment_methods import card_payment
from utils.payment_methods.SiteAPI.payment_statuses import current_payment_status_translated
from utils.states import Payment


@dp.callback_query(F.data == 'payment_method_card', Payment.choosing_method)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id

    key = StorageKey(bot.id, user_id, user_id)
    lang = await users.get_user_lang(user_id)

    data = await storage.get_data(key)
    amount = data.get('amount')
    amount_with_commission = data.get('amount_with_commission')

    currency = data.get('currency')
    internal_order_id = await get_internal_order_id(user_id)
    payment_id = f'SW{internal_order_id}'
    text = messages.payment_by_card[lang].format(
        transaction_id=payment_id, amount=f'{amount_with_commission: .2f}', currency=currency, )

    url = await payment_url.get(user_id, payment_id, amount)
    payment_info = build_payment_info(user_id, amount_rub=amount_with_commission, currency='RUB',
                                      amount_original=amount,
                                      payment_url=url, balance_recharge=True)

    await admin.save_payment(payment_id, payment_info)

    kb = card_payment(lang, url, payment_id, balance_recharge=True)
    await query.message.answer(text, reply_markup=kb.as_markup())
    await query.answer()
    await query.message.delete()
    await state.set_state(None)


# Check Payment

template = callback_templates.balance_recharge()


@dp.callback_query(F.data.startswith(template))
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = await users.get_user_lang(user_id)
    payment_id = query.data.replace(template, '')

    try:
        status = await payment_status.get(payment_id)

    except Exception as e:
        print(f'Error checking payment status for {payment_id}: {e}')
        await query.message.answer(messages.cannot_check_payment_status[lang])
        await query.answer()
        return
    status_msg_ids = []

    if not status:
        await query.answer()
        return

    if status != 'successful':
        text = (f'{messages.current_payment_status[lang]}:\n\n'
                f'{current_payment_status_translated[status][lang]}')

        msg = await query.message.answer(text)
        status_msg_ids.append(msg.message_id)
        await query.answer()
        return

    if not await admin.is_not_paid(payment_id):
        text = messages.balance_recharge_already_paid[lang]
        await query.message.answer(text)
        await query.message.delete()
        return

    payment_info = await admin.get_payment_info(payment_id)

    if payment_info:
        amount = payment_info.get('amount_rub')
        # recharge_commission = admin.get_balance_recharge_commission()
        # if recharge_commission:
        #     amount = await get_amount_minus_commission(amount, recharge_commission)
        # else:
        #     amount = amount

        await _add_balance(user_id, amount, payment_id)
        await admin.update_payment_status(payment_id, status)
        await admin.move_to_successful_payments(payment_id)
        currency = 'RUB'

        formatted_amount = f'{amount:.2f}'
        await query.message.answer(
            messages.balance_recharge_successfully_paid[lang].format(amount=formatted_amount, currency=currency))
        await query.message.delete()

    if status_msg_ids:
        await bot.delete_messages(user_id, status_msg_ids)

    await navigation.return_to_menu(user_id, state)
    await query.answer()


async def _add_balance(user_id: int, amount: float, payment_id: str):
    await users.add_balance(user_id, amount)
    inviter_id = await users.get_inviter_id(user_id)
    if inviter_id:
        await add_referral_reward(inviter_id, amount, referral_id=user_id, payment_id=payment_id)

    user_balance = await users.get_balance(user_id)
    transaction_item = TransactionItem(
        user_id=user_id,
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        balance_after=round((user_balance + amount), 2),
        meta={"payment_id": payment_id}
    )
    await transactions.save(transaction_item)
