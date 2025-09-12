import config
from busines_logic.process_orders.tg_stars_order import InsufficientBalanceError, OrderProcessingError
from core.db import admin, orders as orders_db, users
from core.db.main_orders_que import orders_queue
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus
from loader import bot
from utils import api


async def process_standard_order(order_item: OrderItem):
    available_balance = await api.get_account_balance()
    if available_balance < order_item.amount_without_commission:
        text = (f'<b>Недостаточно средств для оформления заказов.</b>\n'
                f'Текущий баланс: <b>{available_balance:.2f} руб.</b>\n'
                f'Необходимо пополнить счет еще минимум на <b>{round((order_item.amount_without_commission - available_balance), 2)} руб.</b>')
        raise InsufficientBalanceError(text)

    backend_order_id = await create_order(order_item)
    if not backend_order_id:
        raise OrderProcessingError(f'Не удалось оформить заказ{order_item.internal_order_id}. Ошибка API')

    order_item.backend_order_id = backend_order_id
    order_item.order_status = OrderStatus.IN_PROGRESS
    orders_queue.update(order_item)

    # TODO : через время поменять сигнатуру методов под order_item
    admin.remove_order_from_execution_queue(order_item.internal_order_id)
    orders_db.remove_not_accepted_order(order_item.user_id, order_item.internal_order_id)
    # ------       ------        ------        ------        ------


async def create_order(order_item: OrderItem):
    user_id = order_item.user_id
    service_id = order_item.service_id
    url = order_item.url
    quantity = order_item.quantity

    platform = users.get_user_platform(user_id)

    backend_order_id = await api.create_new_order(user_id, str(service_id), url, quantity)

    if backend_order_id is None:
        await bot.send_message(config.ADMIN_ID,
                               f"Не удалось создать заказ {order_item.internal_order_id}. backend_order_id is None")
        return

    order_item.backend_order_id = backend_order_id
    orders_db.new_order(platform, order_item)

    return backend_order_id
