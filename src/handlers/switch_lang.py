from aiogram import types, F
from aiogram.filters import Command

from loader import dp
from core.db import users
from utils import texts, kb
from utils.lang import default_language
from utils.navigation import return_to_menu
from utils.texts import switch_lang


@dp.callback_query(F.data.startswith('select'))
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    data = query.data
    print(data)
    data = query.data.split('_')
    lang_code = data[1]
    print(lang_code)
    users.switch_lang(user_id, lang_code)
    await query.answer(switch_lang[lang_code], show_alert=True)
    await return_to_menu(user_id)
    await query.message.delete()
