from core.db import users
from loader import bot
from utils import texts, kb


async def return_to_menu(_id: int):
    lang = users.get_user_lang(_id)
    await bot.send_message(_id, texts.plans[lang], reply_markup=kb.get_plans(lang).as_markup())

