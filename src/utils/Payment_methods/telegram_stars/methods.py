from aiogram.types import LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.db import users
from core.localisation.texts import buttons
from loader import bot

CURRENCY = 'XTR'


def telegram_stars_btn(lang: str, amount: int):
    builder = InlineKeyboardBuilder()
    text = buttons.telegram_star_pay[lang].format(amount=amount)

    builder.button(text=text, pay=True)
    return builder.as_markup()


async def send_invoice(chat_id: int, title: str, description: str, payload: str, amount: int):
    """
    args:
        chat_id: ID of the chat where the invoice will be sent
        payload: unique string identifier for the invoice
        amount: amount in XTR to be charged
    """
    lang = users.get_user_lang(chat_id)
    prices = [LabeledPrice(label=title, amount=amount)]

    return await bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token='',
        currency=CURRENCY,
        prices=prices,
        reply_markup=telegram_stars_btn(lang, amount)
    )

