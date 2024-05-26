from aiogram import types, F

from core.localisation.texts import messages
from loader import dp
from core.db import users
from utils import kb, callback_templates
from utils.category_names import get_category_name

callback_template = callback_templates.categories()


@dp.callback_query(F.data.startswith(callback_template))
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)

    category = query.data.replace(callback_template, '')

    category_name = get_category_name(category)
    reply_markup = kb.get_services(lang, category_name, user_id).as_markup()

    await query.message.answer(messages.get_plans[lang], reply_markup=reply_markup)
    await query.answer()
    await query.message.delete()

