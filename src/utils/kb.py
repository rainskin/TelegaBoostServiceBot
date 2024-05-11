from aiogram.utils.keyboard import InlineKeyboardBuilder
from . import plans
from .lang import lang_names, lang_codes


def get_plans(def_lang: str):
    builder = InlineKeyboardBuilder()
    count = 0
    for name in plans.names[def_lang]:
        callback_data = f"plan_{plans.names['sys'][count]}"
        builder.button(text=name, callback_data=callback_data)
        count += 1

    return builder.adjust(1)

def select_lang(def_lang: str):
    builder = InlineKeyboardBuilder()
    count = 0
    for lang in lang_names:
        callback_data = f'select_{lang_codes[count]}_lang'
        builder.button(text=lang, callback_data=callback_data)
        count += 1
    return builder.adjust(2)
