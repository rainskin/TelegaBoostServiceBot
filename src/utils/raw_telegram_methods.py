import asyncio

import aiohttp

import config


async def send_message(user_id, text: str):
    url = f'https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage?chat_id={user_id}&text={text}'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.json()

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print('Error sending message:', str(e))