from aiogram.utils.deep_linking import create_start_link

from loader import bot


async def create(user_id: int):
    link = await create_start_link(bot, f'ref{str(user_id)}')
    return link

