from aiogram import types

from loader import bot


async def delete_messages(chat_id: int, msgs_to_delete: list[int]):
    for msg_id in msgs_to_delete:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            print(f"Error deleting message {msg_id}: {e}")


