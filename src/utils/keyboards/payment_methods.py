from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.localisation.texts import buttons
from utils import callback_templates


def bank_card_btn(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.payment_method_card[lang]
    callback = buttons.payment_method_card['callback']

    builder.button(text=text, callback_data=callback)
    return builder


def internal_balance_btn(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.payment_method_internal_balance[lang]
    callback = buttons.payment_method_internal_balance['callback']

    builder.button(text=text, callback_data=callback)
    return builder


def telegram_stars_btn(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.payment_method_telegram_stars[lang]
    callback = buttons.payment_method_telegram_stars['callback']

    builder.button(text=text, callback_data=callback)
    return builder


def kb(lang: str, from_balance=False, from_card=False, from_telegram_stars=False) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    if from_card:
        builder.attach(bank_card_btn(lang))

    if from_balance:
        builder.attach(internal_balance_btn(lang))

    if from_telegram_stars:
        builder.attach(telegram_stars_btn(lang))

    return builder


def card_payment(lang: str, payment_url: str, order_id: str, balance_recharge=False):
    builder = InlineKeyboardBuilder()

    builder.button(text=buttons.card_pay[lang], url=payment_url)
    if balance_recharge:
        callback_template = callback_templates.balance_recharge()
    else:
        callback_template = callback_templates.check_payment()

    callback_data = f'{callback_template}{order_id}'

    builder.button(text=buttons.check_pay[lang], callback_data=callback_data)
    builder.adjust(1)

    return builder
