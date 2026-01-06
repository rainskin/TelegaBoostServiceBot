from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.db.models.order_item import OrderItem
from core.localisation.texts import unpaid_order_summary, messages
from core.localisation.texts.buttons import buy_stars_button
from core.storage import storage
from enums.orders.service_type import ServiceType
from handlers.new_order.create import save_unpaid_order
from handlers.new_order.st4_make_order import get_internal_order_id
from loader import bot, dp
from utils import states
from utils.callback_templates import balance_recharge_template
from utils.keyboards import unpaid_orders
from utils.methods import delete_messages
from utils.navigation import return_to_menu


@dp.callback_query(F.data == 'yes', states.BuyStars.confirmation)
async def handle_payment(query: types.CallbackQuery, state: FSMContext):
    user_id = query.message.chat.id
    lang = await users.get_user_lang(user_id)
    key = StorageKey(bot.id, user_id, user_id)
    data = await storage.get_data(key)

    msgs_to_delete = data.get('msgs_to_delete', [])
    internal_order_id = await get_internal_order_id(user_id)


    total_amount = data.get('total_amount')
    amount_without_commission = data.get('amount_without_commission')
    profit = data.get('profit')

    order_item = OrderItem(
        internal_order_id=internal_order_id,
        user_id=user_id,
        service_type=ServiceType.TG_STARS,
        service_id=None,
        service_name='⭐ Telegram Stars',
        url=data.get('recipient'),
        quantity=data.get('quantity'),
        amount_without_commission=amount_without_commission,
        total_amount=total_amount,
        profit=profit
    )

    await save_unpaid_order(order_item)

    currency = "RUB"
    order_summary_text = unpaid_order_summary.TG_STARS_ORDER[lang].format(internal_order_id=internal_order_id,
                                                                          service_name=order_item.service_name,
                                                                          quantity=order_item.quantity,
                                                                          username=order_item.url,
                                                                          total_amount=order_item.total_amount,
                                                                          currency=currency)
    kb = unpaid_orders.get_keyboard(lang, internal_order_id)
    await query.message.answer(order_summary_text, reply_markup=kb.as_markup())
    await query.answer()

    await delete_messages(user_id, msgs_to_delete)

@dp.callback_query(F.data == 'no', states.BuyStars.confirmation)
async def handle_payment(query: types.CallbackQuery, state: FSMContext):
    user_id = query.message.chat.id
    lang = await users.get_user_lang(user_id)
    key = StorageKey(bot.id, user_id, user_id)
    data = await storage.get_data(key)
    msgs_to_delete = data.get('msgs_to_delete', [])

    await query.answer(messages.cancel_action[lang])
    await delete_messages(user_id, msgs_to_delete)
    await return_to_menu(user_id, state)
