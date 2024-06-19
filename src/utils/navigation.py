from aiogram.fsm.storage.base import StorageKey

import config
from core.db import users
from core.storage import storage
from loader import bot
from utils.keyboards import navigation_kb, categories, admin
from core.localisation.texts import messages


async def return_to_menu(user_id: int):
    lang = users.get_user_lang(user_id)
    user_balance = users.get_balance(user_id)

    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    await storage.delete_data(key)

    if not user_balance:
        msg_text = messages.main_menu[lang]
    else:
        currency = 'RUB'
        user_balance_text = messages.your_balance[lang].format(amount=str(user_balance), currency=currency)
        msg_text = (f'{messages.main_menu[lang]} \n\n'
                    f'{user_balance_text}')

    await bot.send_message(user_id, msg_text, reply_markup=navigation_kb.main_menu(lang).as_markup())


async def get_categories(user_id: int):
    lang = users.get_user_lang(user_id)
    kb = await categories.get_categories(user_id, lang)
    await bot.send_message(user_id, messages.plans[lang], reply_markup=kb.as_markup())


async def get_admin_menu(user_id: int):
    if user_id != config.ADMIN_ID:
        return

    text = f'<b>🧑🏻‍💻 Админ панель:</b>'
    await bot.send_message(user_id, text, reply_markup=admin.admin_menu().as_markup())
