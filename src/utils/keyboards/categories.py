from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils import api, callback_templates
from core.localisation.lang import lang_names, lang_codes
from core.localisation.texts import buttons
from utils.keyboards.navigation_kb import navigation


def get_categories(lang: str):
    builder = InlineKeyboardBuilder()

    for name, callback in zip(buttons.categories[lang], buttons.categories['callbacks']):
        callback_data = f"{callback_templates.categories()}{callback}"
        builder.button(text=name, callback_data=callback_data)

    builder.adjust(1)
    builder.attach(navigation(lang, menu_button=True))
    return builder


async def get_services(lang: str, category_name: str, user_id: int):
    builder = InlineKeyboardBuilder()
    tariffs = await api.get_tariffs(category_name, user_id)
    for tariff in tariffs:
        text = tariff['name']
        _id = tariff['service']
        callback = f'{callback_templates.services()}{_id}'

        builder.button(text=text, callback_data=callback)

    builder.adjust(1)
    builder.attach(navigation(lang, menu_button=True))

    return builder
