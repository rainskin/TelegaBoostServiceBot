from aiogram import types

from loader import bot


async def delete_messages(chat_id: int, msgs_to_delete: list[int]):
    for msg_id in msgs_to_delete:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            print(f"Error deleting message {msg_id}: {e}")


async def safe_delete_callback_message(query: types.CallbackQuery):
    message = query.message
    if message is None:
        return

    if not hasattr(message, 'delete'):
        print(
            "[safe_delete_callback_message] Message is inaccessible, skip delete. "
            f"callback={query.data}"
        )
        return

    try:
        await message.delete()
    except Exception as e:
        print(
            "[safe_delete_callback_message] Failed to delete message. "
            f"callback={query.data}, error={e}"
        )