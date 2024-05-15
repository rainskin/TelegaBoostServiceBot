from aiogram import types, F

from loader import dp
from utils import navigation


@dp.callback_query(F.data == 'back_to_menu')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    await navigation.return_to_menu(user_id)
    await query.answer()
    await query.message.delete()

@dp.callback_query(F.data == 'back')
async def _(query: types.CallbackQuery):
    await query.answer('эта кнопка пока не работает')




