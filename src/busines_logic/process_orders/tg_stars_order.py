from core.db import admin, orders as orders_db
from core.db.main_orders_que import orders_queue
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus


def process_tg_stars_order(order_item: OrderItem):
    print(f"Skipping non-standard service type for order {order_item.internal_order_id}")
    order_item.order_status = OrderStatus.CANCELED
    order_item.deleted = True
    orders_queue.update(order_item)
    admin.remove_order_from_execution_queue(order_item.internal_order_id)
    orders_db.remove_not_accepted_order(order_item.user_id, order_item.internal_order_id)
