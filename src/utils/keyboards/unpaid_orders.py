from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callback_templates import pay_unpaid_order_template, delete_unpaid_order_template

pay_unpaid_order_button_text = {
    'ru': 'Оплатить заказ',
    'en': 'Pay for the order',
}

delete_unpaid_order_button_text = {
    'ru': 'Удалить заказ',
    'en': 'Delete order',
}


def pay_button(lang: str, internal_order_id: str):
    template = pay_unpaid_order_template()
    builder = InlineKeyboardBuilder()
    text = pay_unpaid_order_button_text[lang]
    callback = f'{template}{internal_order_id}'

    builder.button(text=text, callback_data=callback)
    return builder


def delete_button(lang: str, internal_order_id: str):
    builder = InlineKeyboardBuilder()
    template = delete_unpaid_order_template()
    text = delete_unpaid_order_button_text[lang]
    callback = f'{template}{internal_order_id}'

    builder.button(text=text, callback_data=callback)
    return builder


def get_keyboard(lang: str, internal_order_id: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.attach(pay_button(lang, internal_order_id))
    builder.attach(delete_button(lang, internal_order_id))

    return builder
