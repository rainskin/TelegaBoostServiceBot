from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import api, callback_templates
from core.localisation.lang import lang_names, lang_codes
from core.localisation.texts import buttons


def get_categories(lang: str):
    builder = InlineKeyboardBuilder()

    for name, callback in zip(buttons.categories[lang], buttons.categories['sys']):
        callback_data = f"{callback_templates.categories()}{callback}"
        builder.button(text=name, callback_data=callback_data)

    builder.adjust(1)
    builder.attach(navigation(lang, menu_button=True))
    return builder


def select_lang():
    builder = InlineKeyboardBuilder()
    for lang_name, lang_code in zip(lang_names, lang_codes):
        callback_data = f'{callback_templates.select_lang()}{lang_code}'
        builder.button(text=lang_name, callback_data=callback_data)
    return builder.adjust(2)


def main_menu(lang: str):
    builder = InlineKeyboardBuilder()
    texts: List[str] = buttons.main_menu[lang]
    callbacks: List[str] = buttons.main_menu['sys']
    for (text, callback_data) in zip(texts, callbacks):
        builder.button(text=text, callback_data=callback_data)

    builder.attach(change_language(lang))
    return builder.adjust(2)


def change_language(lang: str):
    builder = InlineKeyboardBuilder()
    text = buttons.change_language[lang]
    callback_data = buttons.change_language['sys']

    for (text, callback_data) in zip(text, callback_data):
        builder.button(text=text, callback_data=callback_data)

    return builder


def navigation(lang: str, menu_button=False, back_button=False):
    builder = InlineKeyboardBuilder()
    texts = buttons.navigation_menu[lang]
    callbacks = buttons.navigation_menu['sys']

    buttons_data = [menu_button, back_button]
    button_indices = [index for index, is_enabled in enumerate(buttons_data) if is_enabled]

    for index in button_indices:
        text = texts[index]
        callback_data = callbacks[index]
        builder.button(text=text, callback_data=callback_data)

    return builder.adjust(2)


def get_plans(lang: str, category_name: str):
    builder = InlineKeyboardBuilder()
    tariffs = api.get_tariffs(category_name)
    for tariff in tariffs:
        text = tariff['name']
        _id = tariff['service']
        callback = f'{callback_templates.plans()}{_id}'

        builder.button(text=text, callback_data=callback)

    builder.adjust(1)
    builder.attach(navigation(lang, menu_button=True))

    return builder
