from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class NewOrder(StatesGroup):
    choosing_quantity = State()
    waiting_for_url = State()
    