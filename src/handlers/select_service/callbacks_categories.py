from aiogram import types, F

from core.localisation.texts import messages
from loader import dp
from core.db import users
from utils import callback_templates
from busines_logic import special_offers
from utils.keyboards import categories
from utils.category_names import get_category_name
from utils.keyboards.navigation_kb import navigation

callback_template = callback_templates.categories()


@dp.callback_query(F.data.startswith(callback_template))
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)

    category = query.data.replace(callback_template, '')

    if category == 'hot_offers':
        reply_markup = special_offers.get_special_offers_keyboard(lang).attach(navigation(lang, menu_button=True))
    else:
        category_name = get_category_name(category)
        reply_markup = await categories.get_services(lang, category_name, user_id)
    await query.message.answer(messages.get_plans[lang], reply_markup=reply_markup.as_markup())
    await query.answer()
    await query.message.delete()

