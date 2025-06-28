import asyncio

from busines_logic.order_managment.take_into_work import try_take_orders_into_work_repeatedly


async def start():
    asyncio.create_task(try_take_orders_into_work_repeatedly(cooldown=60))