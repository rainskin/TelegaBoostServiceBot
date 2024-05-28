from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils import api, callback_templates
from core.localisation.lang import lang_names, lang_codes
from core.localisation.texts import buttons


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


def kb(lang: str, from_balance=False):
    builder = InlineKeyboardBuilder()
    builder.attach(bank_card_btn(lang))

    if from_balance:
        builder.attach(internal_balance_btn(lang))

    return builder

