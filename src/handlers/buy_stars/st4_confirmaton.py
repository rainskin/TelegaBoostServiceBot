from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.db.models.order_item import OrderItem
from core.localisation.texts.buttons import buy_stars_button
from core.storage import storage
from enums.orders.service_type import ServiceType
from handlers.new_order.create import save_unpaid_order
from handlers.new_order.st4_make_order import get_internal_order_id
from loader import bot, dp
from utils import states
from utils.callback_templates import balance_recharge_template
from utils.keyboards.unpaid_orders import get_keyboard
from utils.methods import delete_messages
from utils.navigation import return_to_menu


@dp.callback_query(F.data == 'yes', states.BuyStars.confirmation)
async def handle_payment(query: types.CallbackQuery, state: FSMContext):
    user_id = query.message.chat.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot.id, user_id, user_id)
    data = await storage.get_data(key)
    for key in data.keys():
        print(f'{key}')

    msgs_to_delete = data.get('msgs_to_delete', [])
    internal_order_id = await get_internal_order_id(user_id)
    kb = get_keyboard(lang, internal_order_id)
    await query.message.answer('подтвердите заказ', reply_markup=kb.as_markup())
    await query.answer()

    total_amount = data.get('total_amount')
    amount_without_commission = data.get('amount_without_commission')
    profit = total_amount - amount_without_commission

    order_item = OrderItem(
        internal_order_id=internal_order_id,
        user_id=user_id,
        service_type=ServiceType.TG_STARS,
        service_id=None,
        service_name='Telegram Stars',
        url=data.get('recipient'),
        quantity=data.get('quantity'),
        amount_without_commission=amount_without_commission,
        total_amount=total_amount,
        profit=profit
    )

    save_unpaid_order(order_item)
    await delete_messages(user_id, msgs_to_delete)

@dp.callback_query(F.data == 'yes', states.BuyStars.confirmation)
async def handle_payment(query: types.CallbackQuery, state: FSMContext):
    user_id = query.message.chat.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot.id, user_id, user_id)
    data = await storage.get_data(key)
    msgs_to_delete = data.get('msgs_to_delete', [])
    await query.answer()
    await delete_messages(user_id, msgs_to_delete)
    await return_to_menu(user_id, state)
