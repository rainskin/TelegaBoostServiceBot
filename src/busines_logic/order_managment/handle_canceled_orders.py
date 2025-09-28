import config
from core.db import orders, users
from core.db.main_orders_queue import orders_queue
from core.db.models.transaction_item import TransactionItem
from core.db.transactions import transactions
from core.localisation.texts import messages
from enums.orders.order_status import OrderStatus
from enums.transaction_type import TransactionType
from loader import bot


async def return_money_for_canceled_or_partial_order(user_id: int, backend_order_id: str, order_status_info: dict):
    status = order_status_info['status']
    notification_for_user_text = ''
    notification_for_admin_text = ''
    currency = 'RUB'

    full_order_info = orders.get_order_info(user_id, backend_order_id, current_orders=True)
    internal_order_id = full_order_info['internal_order_id']
    if status == "Canceled":

        amount = full_order_info['total_amount']

        await update_db(user_id, backend_order_id, internal_order_id, amount, status)
        lang = users.get_user_lang(user_id)
        notification_for_user_text = messages.order_was_canceled[lang].format(internal_order_id=internal_order_id, amount=amount, currency=currency)
        notification_for_admin_text = f'типа вернул {amount} за заказ {internal_order_id} ({backend_order_id}) пользователя {user_id}'
    if status == 'Partial':

        total_amount = full_order_info['total_amount']
        quantity = full_order_info['quantity']

        # TODO: хорошо бы remains тоже в бд держать
        remains = int(order_status_info['remains'])

        cost_per_one_execution = total_amount / quantity
        amount = cost_per_one_execution * remains
        internal_order_id = full_order_info['internal_order_id']
        notification_for_admin_text = (f'Оформляю возврат за частично выполненный заказ:\n\n'
                f'Заказ: {internal_order_id} ({backend_order_id}), ID пользователя: {user_id}\n\n'
                f'Количество: {quantity}\n'
                f'На сумму: {total_amount}\n'
                f'Остаток: {remains} единиц\n'
                f'Цена одного выполнения: {cost_per_one_execution}\n\n'
                f'Возвращаю пользователю: {amount}')

        notification_for_user_text = f'Заказ <b>{internal_order_id}</b> выполнен частично. Возвращено на баланс: {amount} {currency}'

        await update_db(user_id, backend_order_id, internal_order_id, amount, status)
    try:
        if notification_for_admin_text:
            await bot.send_message(config.ADMIN_ID, notification_for_admin_text)
        if notification_for_user_text:
            await bot.send_message(user_id, notification_for_user_text)
    except Exception as e:
        pass




async def update_db(user_id: int, backend_order_id: str, internal_order_id: str, amount: float, order_status: str):
    meta = {
        "order_id": backend_order_id,
        "note": f"Refund for {order_status} order"}
    try:
        order_item = orders_queue.get(internal_order_id)
        order_item.order_status = OrderStatus.CANCELED if order_status == 'Canceled' else OrderStatus.PARTIAL
        order_item.is_money_returned = True
        orders_queue.update(order_item)
    except Exception:
        pass

    orders.return_money_for_current_order(user_id, backend_order_id, amount)

    user_balance = users.get_balance(user_id)

    transaction_item = TransactionItem(
        user_id=user_id,
        transaction_type=TransactionType.REFUND,
        amount=amount,
        balance_after=round((user_balance + amount), 2),
        meta=meta
    )
    await transactions.save(transaction_item)



async def remove_orders_to_history_and_return_money_for_canceled_orders(user_id: int, _orders: dict):
    for order_id, order_status_info in _orders.items():
        status = order_status_info['status']

        await return_money_for_canceled_or_partial_order(user_id, order_id, order_status_info)

        if status != 'In progress' and status != 'Awaiting':
            orders.move_orders_to_archive(user_id, order_id)


# async def remove_orders_to_history_and_return_money_for_canceled_orders(user_id: int, backend_order_id: str, order_status_info: dict):
#
#     await return_money_for_canceled_or_partial_order(user_id, backend_order_id, order_status_info)
#
#     status = order_status_info['status']
#     if status != 'In progress' and status != 'Awaiting':
#         orders.move_orders_to_archive(user_id, backend_order_id)


# def update_order_status(user_id: int, backend_order_id: str, status: str):
#     status_mapping = {
#         'In progress': OrderStatus.IN_PROGRESS,
#         'Completed': OrderStatus.COMPLETED,
#         'Awaiting': OrderStatus.AWAITING,
#         'Canceled': OrderStatus.CANCELED,
#         'Fail': OrderStatus.FAIL,
#         'Partial': OrderStatus.PARTIAL
#
#     }
#     status: OrderStatus = status_mapping.get(status)
#
#     # Update in user's orders
#     orders.update_order_status(backend_order_id, status)
#
#     # Update in main orders queue
#     internal_order_id = orders.get_internal_order_id_by_backend_order_id(user_id, backend_order_id)
#     order_item = orders_queue.get(internal_order_id)
#     order_item.order_status = status
#     orders_queue.update(order_item)


def update_statuses(user_id: int, order_statuses: dict):
    status_mapping = {
        'In progress': OrderStatus.IN_PROGRESS,
        'Completed': OrderStatus.COMPLETED,
        'Awaiting': OrderStatus.AWAITING,
        'Canceled': OrderStatus.CANCELED,
        'Fail': OrderStatus.FAIL,
        'Partial': OrderStatus.PARTIAL

    }

    for backend_order_id, order_status_info in order_statuses.items():
        status = order_status_info['status']

        status: OrderStatus = status_mapping.get(status)


        # Update in main orders queue
        internal_order_id = orders.get_internal_order_id_by_backend_order_id(user_id, backend_order_id)
        order_item = orders_queue.get(internal_order_id)
        order_item.order_status = status
        orders_queue.update(order_item)

        # Update in user's orders
        order_item = orders_queue.get(internal_order_id)
        orders.update_active_order(backend_order_id, order_item)
