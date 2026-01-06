import asyncio

from busines_logic.order_managment import update_status_of_orders
from busines_logic.order_managment.take_into_work import try_take_orders_into_work_repeatedly


async def start():
    pass
    asyncio.create_task(try_take_orders_into_work_repeatedly(cooldown=60))
    asyncio.create_task(update_status_of_orders.run_repeatedly(cooldown=600))
    # asyncio.create_task(try_place_paid_orders_repeatedly(cooldown=10))
