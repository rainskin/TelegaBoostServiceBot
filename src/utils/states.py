from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class NewOrder(StatesGroup):
    choosing_quantity = State()
    waiting_for_url = State()
    check_details = State()


class BalanceRecharge(StatesGroup):
    choosing_amount = State()

class ManageOrder(StatesGroup):
    cancel_order = State()


class Payment(StatesGroup):
    choosing_method = State()


class AdminStates(StatesGroup):
    to_take_orders_into_work = State()
