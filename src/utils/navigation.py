from core.db import users
from loader import bot
from utils.keyboards import navigation_kb, categories
from core.localisation.texts import messages


async def return_to_menu(user_id: int):
    lang = users.get_user_lang(user_id)
    user_balance = users.get_balance(user_id)

    if not user_balance:
        msg_text = messages.main_menu[lang]
    else:
        currency = 'RUB'
        user_balance_text = messages.your_balance[lang].format(amount=str(user_balance), currency=currency)
        msg_text = (f'{messages.main_menu[lang]} \n\n'
                    f'{user_balance_text}')

    await bot.send_message(user_id, msg_text, reply_markup=navigation_kb.main_menu(lang).as_markup())


async def get_categories(_id: int):
    lang = users.get_user_lang(_id)
    await bot.send_message(_id, messages.plans[lang], reply_markup=categories.get_categories(lang).as_markup())

