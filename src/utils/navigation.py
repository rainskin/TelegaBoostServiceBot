from core.db import users
from loader import bot
from utils import kb
from utils.texts import messages


async def return_to_menu(_id: int, lang: str):
    await bot.send_message(_id, messages.main_menu[lang], reply_markup=kb.main_menu(lang).as_markup())


async def get_plans(_id: int, lang: str):
    await bot.send_message(_id, messages.plans[lang], reply_markup=kb.get_plans(lang).as_markup())

