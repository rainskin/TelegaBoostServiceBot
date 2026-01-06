from aiogram import types
from aiogram.filters import Command, CommandObject

import config
from core.db import users
from core.localisation.texts import messages
from loader import dp


@dp.message(Command('support'))
async def _(msg: types.Message, command: CommandObject):
    user_id = msg.from_user.id
    lang = await users.get_user_lang(user_id)

    support_contact = config.SUPPORT_BOT_URL

    await msg.answer(messages.support_contact[lang].format(support_contact=support_contact))