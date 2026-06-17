from busines_logic.process_orders.tg_stars_order import InsufficientBalanceError
from core.db import admin, orders as orders_db, users
from core.db.main_orders_queue import orders_queue
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus
from utils import api


class OrderProcessingAlreadyLoggedError(Exception):
    pass


async def process_standard_order(order_item: OrderItem):
    available_balance = await api.get_account_balance()
    if available_balance < order_item.amount_without_commission:
        text = (f'<b>Недостаточно средств для оформления заказов.</b>\n'
                f'Текущий баланс: <b>{available_balance:.2f} руб.</b>\n'
                f'Необходимо пополнить счет еще минимум на <b>{round((order_item.amount_without_commission - available_balance), 2)} руб.</b>')
        raise InsufficientBalanceError(text)

    backend_order_id = await create_order(order_item)
    if not backend_order_id:
        raise OrderProcessingAlreadyLoggedError(order_item.internal_order_id)

    order_item.backend_order_id = backend_order_id
    order_item.order_status = OrderStatus.IN_PROGRESS

    # сохранение заказа в current_orders
    platform = await users.get_user_platform(order_item.user_id)
    await orders_db.new_order(platform, order_item)

    await orders_queue.update(order_item)

    # TODO : через время поменять сигнатуру методов под order_item
    await admin.remove_order_from_execution_queue(order_item.internal_order_id)
    await orders_db.remove_not_accepted_order(order_item.user_id, order_item.internal_order_id)
    # ------       ------        ------        ------        ------


async def create_order(order_item: OrderItem):
    service_id = order_item.service_id
    url = order_item.url
    quantity = order_item.quantity

    try:
        return await api.create_new_order(
            str(service_id),
            url,
            quantity,
            provider_service_type=order_item.provider_service_type or api.DEFAULT_PROVIDER_SERVICE_TYPE,
            subscription_posts=order_item.subscription_posts,
            subscription_min=order_item.subscription_min,
            subscription_max=order_item.subscription_max,
        )
    except api.ProviderOrderCreateError as exc:
        order_item.provider_http_status = exc.status_code
        order_item.provider_error_message = exc.provider_message
        order_item.order_status = OrderStatus.FAIL
        await orders_queue.update(order_item)
        raise
