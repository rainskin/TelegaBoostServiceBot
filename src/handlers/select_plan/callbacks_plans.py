from aiogram import types, F

from core.localisation.texts import messages
from loader import dp
from core.db import users
from utils import kb, callback_templates, api
from utils.category_names import get_category_name

callback_template = callback_templates.plans()


def is_correct_info(plan_info):
    return plan_info and ('\n' in plan_info)

@dp.callback_query(F.data.startswith(callback_template))
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)

    plan_id = query.data.replace(callback_template, '')
    plan = api.get_plan(int(plan_id), user_id)

    plan_info: str = plan['description']

    if is_correct_info(plan_info):
        name, description = plan_info.split('\n', 1)
    else:
        name, description = plan['name'], ''

    rate = plan['rate']

    if type(rate) == float:
        rate = round(rate, 2)

    min_count = plan['min']
    max_count = plan['max']
    canceling_is_available = plan['canceling_is_available']

    msg = messages.get_plan_info_text(lang, name, description, rate, min_count, max_count, canceling_is_available)
    await query.message.answer(msg, reply_markup=kb.navigation(lang, menu_button=True).as_markup(), disable_web_page_preview=True)
    await query.answer()
    await query.message.delete()
