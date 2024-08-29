import asyncio
import math
import random

from aiogram import F, types
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import ContentType, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from core.storage import storage
from core.db import users
from loader import dp, bot
from utils import callback_templates
from utils.states import Newsletter


@dp.callback_query(F.data == callback_templates.accept_button_template(), Newsletter.confirm_message)
async def _(query: CallbackQuery, state: FSMContext):
    chat_id = ADMIN_ID

    key = StorageKey(bot.id, chat_id, chat_id)
    data = await storage.get_data(key)
    msg_for_newsletter_id = data.get('msg_for_newsletter_id')

    await state.set_state()
    await query.message.delete()

    user_ids = users.get_all_active_users_ids()
    total_messages_processed = 0
    successfully_sent_messages = 0
    error_count = 0

    total_messages = len(user_ids)
    amount_messages_per_time = 30
    total_of_message_parts = math.ceil(total_messages / amount_messages_per_time)
    number_of_message_parts = 0
    messages_processed = 0
    newsletter_progress_message = await query.message.answer('Начинаю рассылку!')
    for user_id in user_ids:
        try:
            await bot.copy_message(user_id, chat_id, msg_for_newsletter_id)
            successfully_sent_messages += 1

        except TelegramForbiddenError as e:
            error_count += 1
            users.set_active_status(user_id, False)
        except TelegramBadRequest as e:
            print(e.message)
            error_count += 1
            # if 'chat not found' in e.message:
            #     print('чата нет')

        messages_processed += 1
        total_messages_processed += 1

        if messages_processed >= amount_messages_per_time:
            number_of_message_parts += 1
            await newsletter_progress_message.edit_text(
                f'Отправлено пачек: {number_of_message_parts} из {total_of_message_parts}')
            messages_processed = 0
            sleep_time = round(random.random(), 2)
            await asyncio.sleep(sleep_time)

    await newsletter_progress_message.delete()
    await bot.send_message(ADMIN_ID,
                           f'Рассылка завершена! Отправил {total_messages_processed} сообщений. Успешно: {successfully_sent_messages} Заблокировали бота: {error_count}')
