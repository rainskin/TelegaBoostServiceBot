import asyncio
import datetime
from datetime import timezone, timedelta, datetime

from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from loader import dp


@dp.message(Command('start'))
async def _(msg: types.Message):
    await msg.answer('Работаем')

