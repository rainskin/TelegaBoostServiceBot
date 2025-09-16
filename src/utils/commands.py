from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

import config
from core.localisation.texts import commands_description


async def set_commands(lang: str, bot: Bot):
    lang = 'ru'
    commands = [
        BotCommand(
            command='start',
            description=f'{commands_description.start[lang]}'
        ),
        BotCommand(
            command='support',
            description=f'{commands_description.support[lang]}'
        ),
        BotCommand(
            command='buy_stars',
            description=f'{commands_description.buy_stars[lang]}'
        ),
    ]

    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())
