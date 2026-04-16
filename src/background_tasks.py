import asyncio

from busines_logic.order_managment import update_status_of_orders
from busines_logic.order_managment.take_into_work import try_take_orders_into_work_repeatedly


def _log_task_result(task: asyncio.Task, task_name: str):
    try:
        exception = task.exception()
    except asyncio.CancelledError:
        print(f"[background_tasks] Task '{task_name}' was cancelled")
        return

    if exception is not None:
        print(f"[background_tasks] Task '{task_name}' stopped with error: {exception}")


def _create_logged_task(coro, task_name: str):
    task = asyncio.create_task(coro, name=task_name)
    task.add_done_callback(lambda t: _log_task_result(t, task_name))
    print(f"[background_tasks] Started task '{task_name}'")
    return task


async def start():
    _create_logged_task(try_take_orders_into_work_repeatedly(cooldown=60), 'take_orders_into_work')
    _create_logged_task(update_status_of_orders.run_repeatedly(cooldown=600), 'update_status_of_orders')
    # _create_logged_task(try_place_paid_orders_repeatedly(cooldown=10), 'try_place_paid_orders')