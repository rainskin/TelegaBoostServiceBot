from aiogram import F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import LabeledPrice

from core.db import users
from core.db.admin import build_payment_info, admin
from core.localisation.texts import messages
from core.storage import storage
from handlers.new_order.st4_make_order import get_internal_order_id
from handlers.payment_processing.from_card import add_balance
from loader import bot, dp
from utils import states
from utils.Payment_methods.telegram_stars.methods import send_invoice
from utils.callback_templates import balance_recharge_template
from utils.currencies.telegram_stars import convert_to_stars
from utils.navigation import return_to_menu
from aiogram.exceptions import TelegramBadRequest
template = balance_recharge_template()

@dp.callback_query(F.data == 'payment_method_telegram_stars', states.Payment.choosing_method)
async def handle_payment(query: types.CallbackQuery):

    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot.id, user_id, user_id)
    data = await storage.get_data(key)
    amount_in_rub = data.get('amount')
    amount_in_rub_with_commission = data.get('amount_with_commission')
    amount_in_stars = convert_to_stars(amount_in_rub)

    internal_order_id = await get_internal_order_id(user_id)
    payment_id = f'S{internal_order_id}'

    title = messages.balance_recharge_invoice_title[lang]
    description = messages.balance_recharge_invoice_description[lang].format(amount=amount_in_rub_with_commission, currency='RUB')
    payload = f'{template}{payment_id}'

    msg = await send_invoice(user_id, title, description, payload, amount_in_stars)

    payment_info = build_payment_info(user_id, amount_in_rub_with_commission, 'XTR', amount_original=amount_in_stars, payment_url=msg.message_id,  balance_recharge=True)
    admin.save_payment(payment_id, payment_info)
    await query.answer()
    await query.message.delete()


@dp.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: types.PreCheckoutQuery):
    # Here you can add any checks before confirming the payment
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except TelegramBadRequest as e:
        print(f"Error answering pre-checkout query: {e}")


@dp.message(F.successful_payment)
async def successful_payment_handler(msg: types.Message, state: FSMContext):
    telegram_payment_charge_id = msg.successful_payment.telegram_payment_charge_id
    payment_id = msg.successful_payment.invoice_payload.replace(template, '')
    payment_info = admin.get_payment_info(payment_id)

    user_id = msg.from_user.id
    lang = users.get_user_lang(user_id)
    invoice_message = int(payment_info.get('payment_url'))
    amount_rub = payment_info.get('amount_rub')
    formatted_amount = f'{amount_rub:.2f}'

    await add_balance(user_id, amount_rub)

    status = 'successful'
    admin.update_payment_status(payment_id, status, telegram_payment_charge_id)
    admin.move_to_successful_payments(payment_id)

    await msg.answer(
        messages.balance_recharge_successfully_paid[lang].format(amount=formatted_amount, currency='RUB'), message_effect_id='5104841245755180586')

    await return_to_menu(user_id, state)
    await bot.delete_message(user_id, invoice_message)


