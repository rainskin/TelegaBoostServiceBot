from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core import db
from core.localisation.texts import messages
from handlers.new_order import create
from loader import dp, bot
from core.db import users
from utils import callback_templates, api
from utils.keyboards import navigation_kb
from busines_logic.special_offers import get_offer_by_tag

callback_template = callback_templates.services()


def is_correct_info(plan_info):
    return plan_info and ('\n' in plan_info)


def get_rate_with_commission(rate: int, service_id: str):

    commission = db.admin.get_commission_percentage(service_id)
    rate = rate * (1 + (commission / 100))
    return round(rate)


@dp.callback_query(F.data.startswith(callback_template))
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)

    service_id = query.data.replace(callback_template, '')
    service = await api.get_service(int(service_id), user_id)

    plan_info: str = service['description']

    if is_correct_info(plan_info):
        name, description = plan_info.split('\n', 1)
    else:
        name, description = service['name'], ''

    old_rate: int | float = service['rate']
    new_rate: int = get_rate_with_commission(old_rate, service_id)
    service_info = {
        'service_id': service_id,
        'old_rate': old_rate,
        'rate': new_rate,
        'min_count': service['min'],
        'max_count': service['max'],
        'canceling_is_available': service['canceling_is_available']
    }

    service_info_text = messages.get_plan_info_text(lang, name, description, service_info)
    await query.message.answer(service_info_text,
                               reply_markup=navigation_kb.navigation(lang, menu_button=True).as_markup(),
                               disable_web_page_preview=True)

    storage_key = StorageKey(bot.id, query.message.chat.id, user_id)
    await create.start_creating_new_order(lang, storage_key, state, service_info)

    await query.answer()
    await query.message.delete()


callback_template_special_offer = callback_templates.special_offers()


@dp.callback_query(F.data.startswith(callback_template_special_offer))
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)

    tag = query.data.replace(callback_template_special_offer, '')
    service = get_offer_by_tag(tag)

    name = service.name
    description: str = service.info

    service_info = {
        'price': service.price,
        'amount_without_commission': service.amount_without_commission,
        'services_and_amount': service.services_and_amount,
        'profit': service.profit,
        'canceling_is_available': service.canceling_is_available
    }

    service_info_text = messages.get_plan_info_text(lang, name, description, service_info, hot_offer=True)
    await query.message.answer(service_info_text,
                               reply_markup=navigation_kb.navigation(lang, menu_button=True).as_markup(),
                               disable_web_page_preview=True)

    storage_key = StorageKey(bot.id, query.message.chat.id, user_id)
    await create.start_creating_new_hot_order(lang, storage_key, state, service_info)

    await query.answer()
    await query.message.delete()
