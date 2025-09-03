from core.db import admin, orders as orders_db, users
from core.db.main_orders_que import orders_queue
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus
from utils import api


async def process_standard_order(order_item: OrderItem):
    print('начало оформления')
    print(order_item.dict())
    backend_order_id = await create_order(order_item)
    print('оформление завершено')
    print(backend_order_id)

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
    order_item.backend_order_id = backend_order_id
    orders_db.new_order(platform, order_item)

    return backend_order_id
