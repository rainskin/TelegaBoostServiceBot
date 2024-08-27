from aiogram import F, types
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext

from core.storage import storage
from loader import dp, bot
from utils.keyboards.navigation_kb import accept_button
from utils.states import Newsletter


@dp.message(Newsletter.wait_for_message)
async def _(msg: types.Message, state: FSMContext):
    if msg.media_group_id:
        await msg.answer('Альбомы не поддерживаются, отправь обычное сообщение с одним медиа')
        return

    chat_id = msg.from_user.id
    msg_for_newsletter = await bot.copy_message(chat_id, chat_id, msg.message_id)
    kb = await accept_button()
    await msg.answer('⬆️ Сообщение будет выглядеть так. Нажми на кнопку, чтобы начать рассылку', reply_markup=kb)
    key = StorageKey(bot.id, chat_id, chat_id)
    await storage.update_data(key, msg_for_newsletter_id=msg_for_newsletter.message_id)
    await state.set_state(Newsletter.confirm_message)
