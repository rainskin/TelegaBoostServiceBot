from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from .lang import lang_names, lang_codes
from .texts import buttons


def get_plans(def_lang: str):
    builder = InlineKeyboardBuilder()
    count = 0
    for name in buttons.names[def_lang]:
        callback_data = f"plan_{buttons.names['sys'][count]}"
        builder.button(text=name, callback_data=callback_data)
        count += 1

    return builder.adjust(1)


def select_lang():
    builder = InlineKeyboardBuilder()
    count = 0
    for lang in lang_names:
        callback_data = f'select_{lang_codes[count]}_lang'
        builder.button(text=lang, callback_data=callback_data)
        count += 1
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
