from aiogram import types
from aiogram.filters import Command

from core.db import users
from loader import dp
from utils import kb
from utils.lang import default_language
from utils.navigation import return_to_menu
from utils.texts import messages


@dp.message(Command('start'))
async def _(msg: types.Message):
    _id = msg.from_user.id
    if users.is_new(_id):
        user_lang_code = msg.from_user.language_code
        lang = default_language(user_lang_code)
        name = msg.from_user.full_name
        await users.register(_id, name, lang)

        await msg.answer(messages.welcome[lang])
        await msg.answer(messages.change_lang[lang], reply_markup=kb.select_lang().as_markup())
    else:
        lang = users.get_user_lang(_id)
        await return_to_menu(_id, lang)
