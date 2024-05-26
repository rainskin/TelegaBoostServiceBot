from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import kb
from utils.states import NewOrder


@dp.callback_query(F.data == 'make_new_order')
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    chat_id = query.message.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    service_msg_ids: list = data['service_msg_ids']

    await query.answer()

    if service_msg_ids:
        await bot.delete_messages(chat_id, service_msg_ids)
        service_msg_ids = []

    msg = await query.message.answer('пук')
    service_msg_ids.append(msg.message_id)
