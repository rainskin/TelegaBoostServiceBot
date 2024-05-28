from aiogram import types
from aiogram.filters import Command

from core.db import users, promo
from loader import dp
from utils.keyboards import navigation_kb
from core.localisation.lang import default_language
from utils.navigation import return_to_menu
from core.localisation.texts import messages


@dp.message(Command('start'))
async def _(msg: types.Message):
    user_id = msg.from_user.id
    if users.is_new(user_id):
        user_lang_code = msg.from_user.language_code
        lang = default_language(user_lang_code)
        name = msg.from_user.full_name
        users.register(user_id, name, lang)

        promo_name = 'balance_for_new_users'

        if not promo.is_completed(promo_name):
            promo.add_participant(promo_name, user_id)

        await msg.answer(messages.welcome[lang])
        await msg.answer(messages.change_lang[lang], reply_markup=navigation_kb.select_lang().as_markup())
    else:
        await return_to_menu(user_id)
