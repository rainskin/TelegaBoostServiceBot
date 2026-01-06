import asyncio

import core.db
import loader


async def main():
    await loader.init_db()
    await core.db.init()

    import background_tasks
    import handlers
    from loader import bot, dp
    from utils import middlewares

    middlewares.setup()
    handlers.setup()
    await background_tasks.start()
    print('bot is running')
    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
