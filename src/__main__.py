import asyncio

import loader


async def main():
    loader.init()

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
