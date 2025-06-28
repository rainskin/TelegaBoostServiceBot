import config
from core.db import orders
from loader import bot


async def return_money_for_canceled_or_partial_order(user_id: int, order_id: str, order_status_info: dict):
    status = order_status_info['status']
    print(status)
    if status == "Canceled":
        full_order_info = orders.get_order_info(user_id, order_id, current_orders=True)
        amount = full_order_info['total_amount']
        orders.return_money_for_current_order(user_id, order_id, amount)
        await bot.send_message(config.ADMIN_ID, f'типа вернул {amount} за заказ {order_id} пользователя {user_id}')
    if status == 'Partial':
        full_order_info = orders.get_order_info(user_id, order_id, current_orders=True)

        total_amount = full_order_info['total_amount']
        quantity = full_order_info['quantity']
        remains = int(order_status_info['remains'])
        print(f'total_amount: {total_amount}, quantity: {quantity}, remains: {remains}')
        cost_per_one_execution = total_amount / quantity
        print(f'remains: {remains}, cost_per_one_execution: {cost_per_one_execution}')
        amount = cost_per_one_execution * remains

        text = (f'Оформляю возврат за частично выполненный заказ:\n\n'
                f'Заказ: {order_id}, ID пользователя: {user_id}\n\n'
                f'Количество: {quantity}\n'
                f'На сумму: {total_amount}\n'
                f'Остаток: {remains} единиц\n'
                f'Цена одного выполнения: {cost_per_one_execution}\n\n'
                f'Возвращаю пользователю: {amount}')

        await bot.send_message(config.ADMIN_ID, text)

        orders.return_money_for_current_order(user_id, order_id, amount)


async def remove_orders_to_history_and_return_money_for_canceled_orders(user_id: int, _orders: dict):
    for order_id, order_status_info in _orders.items():
        status = order_status_info['status']

        await return_money_for_canceled_or_partial_order(user_id, order_id, order_status_info)

        if status != 'In progress' and status != 'Awaiting':
            orders.move_orders_to_archive(user_id, order_id)


