from aiogram.types import LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import bot

CURRENCY = 'XTR'


def telegram_stars_btn():
    builder = InlineKeyboardBuilder()
    text = "Тест 111 ⭐"

    builder.button(text=text, pay=True)
    return builder.as_markup()


async def send_invoice(chat_id: int, amount: int):
    # prices = [LabeledPrice(label='Balance recharge', amount=2),LabeledPrice(label="smth else", amount=1)]
    prices = [LabeledPrice(label='Balance recharge', amount=1)]

    await bot.send_invoice(
        chat_id=chat_id,
        title=f"Пополнение баланса",
        description="описание",
        payload='recharge_balance111',
        provider_token='',
        currency=CURRENCY,
        prices=prices,
        reply_markup=telegram_stars_btn()
    )

    # invoice = await bot.create_invoice_link(
    #     title="test",
    #     description="test test",
    #     payload='recharge_balance',
    #     provider_token='',
    #     currency=CURRENCY,
    #     prices=prices,
    #
    # )
    # print(invoice)
    # эффект огня "5104841245755180586"
