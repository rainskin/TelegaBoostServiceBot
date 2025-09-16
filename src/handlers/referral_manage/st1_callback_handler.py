from aiogram import F, types
from aiogram.fsm.context import FSMContext

from core.db import users, admin
from core.localisation.texts import messages
from loader import dp
from utils.deep_links import referral_link
from utils.keyboards.navigation_kb import navigation


@dp.callback_query(F.data == 'referrals')
async def _(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    link = await referral_link.create(user_id)
    currency = 'RUB'
    reward_percent = admin.get_referral_deposit_reward()
    referral_list = users.get_all_referrals(user_id)
    referral_amount = len(referral_list) if referral_list else 0
    total_earned = users.get_referrals_reward(user_id)
    total_earned_formatted_text = f'{total_earned:.2f}' if total_earned else '0'
    text = (f'{messages.about_referral_system[lang].format(reward_percent=reward_percent, link=link)}\n\n'
            f'{messages.referral_statistics[lang].format(referral_amount=referral_amount, total_earned=total_earned_formatted_text, currency=currency)}')
    await query.message.answer(text, reply_markup=navigation(lang, menu_button=True).as_markup())

    await query.answer()
