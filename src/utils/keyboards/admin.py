from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils import api, callback_templates
from core.localisation.lang import lang_names, lang_codes
from core.localisation.texts import buttons
from utils.category_names import get_category_name
from utils.keyboards.navigation_kb import navigation


def orders_manage():
    builder = InlineKeyboardBuilder()
    builder.button(text='Оформить все заказы', callback_data='to_take_all_orders')
    return builder.adjust(1)


def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text='Заказы', callback_data='manage_orders')
    return builder.adjust(1)
