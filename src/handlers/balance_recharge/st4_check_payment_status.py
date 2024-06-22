from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users, admin
from core.localisation.texts import messages
from core.storage import storage
from handlers.new_order.st4_make_order import get_internal_order_id
from loader import dp, bot
from utils import states, navigation, callback_templates
from utils.Payment_methods.aaio.methods import get_payment_url, check_payment_status
from utils.Payment_methods.aaio.payment_statuses import current_payment_status_translated
from utils.keyboards.payment_methods import card_payment

template = callback_templates.balance_recharge()


@dp.callback_query(F.data.startswith(template))
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    payment_id = query.data.replace(template, '')

    status = await check_payment_status(user_id, payment_id)
    status_msg_ids = []

    successful_payment_status = 'success'

    if not status:
        await query.answer()
        return

    if status != successful_payment_status:

        text = (f'{messages.current_payment_status[lang]}:\n\n'
                f'{current_payment_status_translated[status][lang]}')

        msg = await query.message.answer(text)
        status_msg_ids.append(msg.message_id)
        await query.answer()
        return

    if not admin.is_not_paid(payment_id, successful_payment_status):
        text = messages.balance_recharge_already_paid[lang]
        await query.message.answer(text)
        await query.message.delete()
        return

    payment_info = admin.get_payment_info(payment_id)

    if payment_info:
        amount = payment_info.get('amount')
        users.add_balance(user_id, amount)
        admin.confirm_payment(payment_id, successful_payment_status)
        currency = 'RUB'
        await query.message.answer(messages.balance_recharge_successfully_paid[lang].format(amount=amount, currency=currency))
        await query.message.delete()

    if status_msg_ids:
        await bot.delete_messages(user_id, status_msg_ids)

    await navigation.return_to_menu(user_id, state)
    await query.answer()
