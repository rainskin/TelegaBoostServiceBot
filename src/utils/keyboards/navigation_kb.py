from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.localisation.lang import lang_names, lang_codes
from core.localisation.texts import buttons
from utils import callback_templates


def select_lang():
    builder = InlineKeyboardBuilder()
    for lang_name, lang_code in zip(lang_names, lang_codes):
        callback_data = f'{callback_templates.select_lang()}{lang_code}'
        builder.button(text=lang_name, callback_data=callback_data)
    return builder.adjust(2)


def new_order_button(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.new_order[lang]
    callback = buttons.new_order['callback']

    builder.button(text=text, callback_data=callback)

    return builder


def orders_history(lang):
    builder = InlineKeyboardBuilder()
    text = buttons.orders_history[lang]
    callback = buttons.orders_history['callback']

    builder.button(text=text, callback_data=callback)

    return builder


def current_orders_button(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.current_orders[lang]
    callback = buttons.current_orders['callback']

    builder.button(text=text, callback_data=callback)
    return builder


def continue_button(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.to_continue[lang]
    callback = buttons.to_continue['callback']

    builder.button(text=text, callback_data=callback)
    return builder


def make_order_button(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.make_order_button[lang]
    callback = buttons.make_order_button['callback']

    builder.button(text=text, callback_data=callback)
    return builder


def back_to_categories(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.back_to_categories[lang]
    callback = buttons.back_to_categories['callback']

    builder.button(text=text, callback_data=callback)
    return builder


def change_language(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.change_language[lang]
    callback_data = buttons.change_language['callbacks']

    for (text, callback_data) in zip(text, callback_data):
        builder.button(text=text, callback_data=callback_data)

    return builder


def support(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.support[lang]
    url = buttons.support['url']

    builder.button(text=text, url=url)

    return builder


def main_menu(lang: str):
    builder = InlineKeyboardBuilder()
    current_orders_btn = current_orders_button(lang)
    new_order_btn = new_order_button(lang)
    change_language_btn = change_language(lang)
    support_btn = support(lang)

    builder_buttons = [current_orders_btn, new_order_btn, support_btn, change_language_btn]

    for button in builder_buttons:
        builder.attach(button)
    return builder.adjust(2)


def orders_navigation(current_page: int, amount_pages: int):
    builder = InlineKeyboardBuilder()
    amount_pages = amount_pages if amount_pages > 0 else 1
    if current_page > 1:
        builder.button(text='<<', callback_data='previous_page')
    else:
        builder.button(text='   ', callback_data='___')

    builder.button(text=f'{current_page}/{amount_pages}', callback_data='number_button')

    if current_page < amount_pages:
        builder.button(text='>>', callback_data='next_page')
    else:
        builder.button(text='   ', callback_data='___')

    builder.adjust(3)
    return builder


def orders(lang: str, current_page: int = 0, amount_pages: int = 0, current_orders=True):
    builder = InlineKeyboardBuilder()

    if amount_pages:
        builder.attach(orders_navigation(current_page, amount_pages))

    new_order_btn = new_order_button(lang)
    if current_orders:
        orders_btn = orders_history(lang)
    else:
        orders_btn = current_orders_button(lang)

    builder_buttons = [new_order_btn, orders_btn]

    for button in builder_buttons:
        builder.attach(button)

    builder.attach(navigation(lang, menu_button=True))

    if amount_pages:
        builder.adjust(3, 2, 1)
    else:
        builder.adjust(2, 1)
    return builder


def navigation(lang: str, menu_button=False, back_button=False):
    builder = InlineKeyboardBuilder()
    texts = buttons.navigation_menu[lang]
    callbacks = buttons.navigation_menu['callbacks']

    buttons_data = [menu_button, back_button]
    button_indices = [index for index, is_enabled in enumerate(buttons_data) if is_enabled]

    for index in button_indices:
        text = texts[index]
        callback_data = callbacks[index]
        builder.button(text=text, callback_data=callback_data)

    return builder.adjust(2)


def order_navigation(lang, make_order_btn=False):
    builder = InlineKeyboardBuilder()

    if make_order_btn:
        builder.attach(make_order_button(lang))
    else:
        builder.attach(continue_button(lang))

    builder.attach(back_to_categories(lang))
    builder.attach(navigation(lang, menu_button=True))
    builder.adjust(1, 2)

    return builder


def yes_or_no_kb(lang):
    builder = InlineKeyboardBuilder()
    texts = buttons.yes_or_no[lang]
    callbacks = buttons.yes_or_no['callbacks']

    for (text, callback_data) in zip(texts, callbacks):
        builder.button(text=text, callback_data=callback_data)

    return builder.adjust(2)


def cancel_order(lang, order_id: str):
    builder = InlineKeyboardBuilder()

    callback_template = callback_templates.cancel_order()
    text = buttons.cancel_order[lang]
    callback = f'{callback_template}{order_id}'

    builder.button(text=text, callback_data=callback)
    return builder
