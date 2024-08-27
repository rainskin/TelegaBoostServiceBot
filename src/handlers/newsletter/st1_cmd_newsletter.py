from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from loader import dp
from utils.states import Newsletter


@dp.message(Command('newsletter'))
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id

    if user_id != ADMIN_ID:
        return

    await msg.answer('Отправь сообщение для рассылки\n'
                     '(не альбом)')
    await state.set_state(Newsletter.wait_for_message)
