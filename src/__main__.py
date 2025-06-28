import asyncio

from aiogram.methods import DeleteWebhook

import background_tasks
import handlers
from loader import bot, dp


async def main():
    handlers.setup()
    await background_tasks.start()
    print('bot is running')
    # await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


