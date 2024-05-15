from aiogram import types, F

from loader import dp
from core.db import users
from utils import kb, navigation
from core.localisation.texts import messages


@dp.callback_query(F.data.startswith('orders'))
async def _(query: types.CallbackQuery):
    pass


@dp.callback_query(F.data.startswith('new_order'))
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    await navigation.get_categories(user_id)
    await query.answer()
    await query.message.delete()


@dp.callback_query(F.data == 'change_language')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    await query.message.answer(messages.change_lang[lang], reply_markup=kb.select_lang().as_markup())
    await query.answer()
    await query.message.delete()



