from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder

from busines_logic.special_offers import special_offers_is_available
from utils import api, callback_templates
from core.localisation.lang import lang_names, lang_codes
from core.localisation.texts import buttons
from utils.category_names import get_category_name
from utils.keyboards.navigation_kb import navigation


async def get_categories(user_id, lang: str):
    available_categories = await api.get_available_categories()
    builder = InlineKeyboardBuilder()
    if special_offers_is_available():
        builder.button(text=buttons.hot_offers[lang],
                       callback_data=f"{callback_templates.categories()}{buttons.hot_offers['callback']}")

    for name, callback in zip(buttons.categories[lang], buttons.categories['callbacks']):
        category_is_available = get_category_name(callback) in available_categories
        if category_is_available:
            callback_data = f"{callback_templates.categories()}{callback}"
            builder.button(text=name, callback_data=callback_data)

    builder.adjust(1)
    builder.attach(navigation(lang, menu_button=True))
    return builder


async def get_services(lang: str, category_name: str, user_id: int):
    builder = InlineKeyboardBuilder()
    tariffs = await api.get_services_by_category(category_name)
    for tariff in tariffs:
        text = tariff['name']
        _id = tariff['service']
        callback = f'{callback_templates.services()}{_id}'

        builder.button(text=text, callback_data=callback)

    builder.adjust(1)
    builder.attach(navigation(lang, menu_button=True))

    return builder
