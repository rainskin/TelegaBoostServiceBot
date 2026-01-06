import asyncio

from core.db.main_orders_queue import orders_queue
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus
from handlers.new_order.create import place_order


async def try_place_paid_orders():
    paid_orders = await orders_queue.get_paid_orders()
    if not paid_orders:
        return

    for order in paid_orders:
        await place_paid_order(order)


async def place_paid_order(order: OrderItem):
    order.order_status = OrderStatus.PENDING

    await orders_queue.update(order)
    await place_order(order)


async def try_place_paid_orders_repeatedly(cooldown: int):
    while True:
        await try_place_paid_orders()
        await asyncio.sleep(cooldown)
