from aiogram import types, F

from loader import dp
from core.db import users
from utils import kb
from utils.navigation import return_to_menu
from utils.texts import messages


@dp.callback_query(F.data.startswith('select'))
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    data = query.data.split('_')
    lang_code = data[1]
    users.switch_lang(user_id, lang_code)
    await query.answer(messages.lang_is_changed[lang_code], show_alert=True)
    await return_to_menu(user_id, lang_code)
    await query.message.delete()


@dp.callback_query(F.data == 'change_language')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    await query.message.answer(messages.change_lang[lang], reply_markup=kb.select_lang().as_markup())
    await query.answer()
    await query.message.delete()
