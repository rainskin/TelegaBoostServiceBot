from aiogram import types, F

from loader import dp, bot
from core.db import users
from utils import callback_templates, commands
from utils.navigation import return_to_menu
from core.localisation.texts import messages

callback_template = callback_templates.select_lang()


@dp.callback_query(F.data.startswith(callback_template))
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang_code = query.data.replace(callback_template, '')
    users.switch_lang(user_id, lang_code)
    await query.answer(messages.lang_is_changed[lang_code], show_alert=True)
    await return_to_menu(user_id)
    await query.message.delete()
