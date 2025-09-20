from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from busines_logic.order_managment.handle_canceled_orders import \
    remove_orders_to_history_and_return_money_for_canceled_orders, update_statuses
from core.db import users, orders
from core.db.main_orders_queue import orders_queue
from core.localisation.texts import messages
from core.storage import storage
from enums.orders.service_type import ServiceType
from handlers.callback_handlers.orders_navigation_buttons import get_order_statuses_text, get_order_ids, try_get_orders
from loader import dp, bot
from utils import navigation
from utils.api import get_order_statuses
from utils.keyboards import navigation_kb
from utils.keyboards.navigation_kb import cancel_order
from utils.states import ManageOrders


@dp.callback_query(F.data == 'current_orders')
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    not_accepted_orders = orders.get_not_accepted_orders(user_id)
    if not_accepted_orders:
        await query.message.answer(messages.not_accepted_order[lang])
        for internal_order_id, _order_info in not_accepted_orders.items():
            print(internal_order_id)
            # заказы на звезды не отображаются
            try:
                order_item = orders_queue.get(internal_order_id)
                if order_item.service_type == ServiceType.TG_STARS:
                    continue
                else:
                    print("hello")
            except Exception:
                pass

            url = _order_info.get('url')
            quantity = _order_info.get('quantity')
            total_amount = _order_info.get('total_amount')

            text = messages.not_accepted_order_status[lang].format(order_id=internal_order_id, url=url,
                                                                   quantity=quantity, total_amount=total_amount)
            kb = cancel_order(lang, internal_order_id)
            await query.message.answer(text, reply_markup=kb.as_markup())

    current_orders = True
    _orders = await try_get_orders(user_id, lang, current_orders=current_orders)

    if not _orders:
        await query.message.answer(messages.no_active_orders[lang],
                                   reply_markup=navigation_kb.orders(lang, current_orders=current_orders).as_markup())
        return
    order_ids = get_order_ids(_orders)
    if not order_ids:
        await query.message.answer(messages.no_active_orders[lang],
                                   reply_markup=navigation_kb.orders(lang, current_orders=current_orders).as_markup())
        return

    order_ids = get_orders_without_tg_stars_orders(order_ids)

    if not order_ids:
        await query.message.answer(messages.no_active_orders[lang],
                                   reply_markup=navigation_kb.orders(lang, current_orders=current_orders).as_markup())
        return

    current_order_statuses = await get_order_statuses(order_ids)

    update_statuses(user_id, current_order_statuses)
    await remove_orders_to_history_and_return_money_for_canceled_orders(user_id, current_order_statuses)

    await get_order_statuses_text(user_id, lang, order_ids, current_orders=current_orders)
    await state.set_state(ManageOrders.scroll_orders)
    await storage.set_data(key, current_orders=current_orders, order_ids=order_ids)
    await query.answer()


@dp.callback_query(F.data == 'archive_orders')
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)

    current_orders = False
    _orders = await try_get_orders(user_id, lang, current_orders=current_orders)

    if not _orders:
        await query.message.answer(messages.no_history_of_orders[lang],
                                   reply_markup=navigation_kb.orders(lang, current_orders=current_orders).as_markup())
        return
    order_ids = get_order_ids(_orders)

    if not order_ids:
        await query.message.answer(messages.no_history_of_orders[lang],
                                   reply_markup=navigation_kb.orders(lang, current_orders=current_orders).as_markup())
        return

    order_ids = get_orders_without_tg_stars_orders(order_ids)

    if not order_ids:
        await query.message.answer(messages.no_history_of_orders[lang],
                                   reply_markup=navigation_kb.orders(lang, current_orders=current_orders).as_markup())
        return

    await get_order_statuses_text(user_id, lang, order_ids, current_orders=current_orders)
    await state.set_state(ManageOrders.scroll_orders)
    await storage.set_data(key, current_orders=current_orders, order_ids=order_ids)
    await query.answer()


@dp.callback_query(F.data == 'new_order')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    await storage.delete_data(key)
    await navigation.get_categories(user_id)
    await query.answer()
    await query.message.delete()


@dp.callback_query(F.data == 'change_language')
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)

    await query.message.answer(messages.change_lang[lang], reply_markup=navigation_kb.select_lang().as_markup())
    await query.answer()
    await query.message.delete()


def get_orders_without_tg_stars_orders(order_ids: list[str]):
    for order_id in order_ids:
        try:
            order_item = orders_queue.get(order_id)
            if order_item:
                service_type = order_item.service_type
                if service_type == ServiceType.TG_STARS:
                    order_ids.remove(order_item.internal_order_id)
        except Exception:
            continue

    return order_ids


aboba = \
    {'936845322_N0017168':
         {'creation_date': '12-09-2025 18:16:20', 'updated_at': '12-09-2025 18:16:26',
          'internal_order_id': '936845322_N0017168', 'backend_order_id': None, 'user_id': 936845322,
          'service_type': 'tg_stars', 'service_id': None, 'service_name': '⭐ Telegram Stars', 'url': 'anime_admin',
          'quantity': 300, 'amount_without_commission': 455.56, 'total_amount': 498.0, 'profit': 42.44,
          'canceling_is_available': None, 'order_status': 'pending', 'deleted': False, 'is_money_returned': False},
     '936845322_N0017172':
         {'creation_date': '13-09-2025 19:02:17', 'updated_at': '13-09-2025 19:02:28',
          'internal_order_id': '936845322_N0017172', 'backend_order_id': None, 'user_id': 936845322,
          'service_type': 'tg_stars', 'service_id': None, 'service_name': '⭐ Telegram Stars', 'url': 'anime_admin',
          'quantity': 500, 'amount_without_commission': 758.35, 'total_amount': 812.0, 'profit': 53.65,
          'canceling_is_available': None, 'order_status': 'pending', 'deleted': False, 'is_money_returned': False},
     '936845322_N0017178':
         {'creation_date': '16-09-2025 22:20:00', 'updated_at': '16-09-2025 22:20:05',
          'internal_order_id': '936845322_N0017178', 'backend_order_id': None, 'user_id': 936845322,
          'service_type': 'standard', 'service_id': 214, 'service_name': 'Premium подписчики 7 DAYS', 'url': 'site.com',
          'quantity': 22, 'amount_without_commission': 8.8, 'total_amount': 10.56, 'profit': 1.7599999999999998,
          'canceling_is_available': None, 'order_status': 'pending', 'deleted': False, 'is_money_returned': False}}
