from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.localisation.texts import messages
from handlers.new_order import create
from loader import dp, bot
from core.db import users
from utils import kb, callback_templates, api, states

callback_template = callback_templates.services()


def is_correct_info(plan_info):
    return plan_info and ('\n' in plan_info)


@dp.callback_query(F.data.startswith(callback_template))
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)

    service_id = query.data.replace(callback_template, '')
    service = api.get_service(int(service_id), user_id)

    plan_info: str = service['description']

    if is_correct_info(plan_info):
        name, description = plan_info.split('\n', 1)
    else:
        name, description = service['name'], ''

    rate = service['rate']

    if type(rate) == float:
        rate = round(rate, 2)

    min_count = service['min']
    max_count = service['max']
    canceling_is_available = service['canceling_is_available']

    service_info = messages.get_plan_info_text(lang, name, description, rate, min_count, max_count,
                                               canceling_is_available)
    await query.message.answer(service_info, reply_markup=kb.navigation(lang, menu_button=True).as_markup(),
                               disable_web_page_preview=True)

    storage_key = StorageKey(bot.id, query.message.chat.id, user_id)
    await create.start_creating_new_order(lang, storage_key, state, service_id, rate, min_count, max_count)

    await query.answer()
    await query.message.delete()
