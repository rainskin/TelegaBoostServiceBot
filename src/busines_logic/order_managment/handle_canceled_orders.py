import config
from core.db import orders, users
from core.db.main_orders_queue import orders_queue
from core.db.models.transaction_item import TransactionItem
from core.db.transactions import transactions
from core.localisation.texts import messages
from enums.orders.order_status import OrderStatus
from enums.transaction_type import TransactionType
from loader import bot
from utils import raw_telegram_methods


# async def return_money_for_canceled_or_partial_order(user_id: int, backend_order_id: str, order_status_info: dict):
#     status = order_status_info['status']
#     notification_for_user_text = ''
#     notification_for_admin_text = ''
#     currency = 'RUB'
#
#     print(f"Processing refund for user_id: {user_id}, backend_order_id: {backend_order_id}, status: {status}")
#     full_order_info = await orders.get_order_info(user_id, backend_order_id, current_orders=True)
#     internal_order_id = full_order_info['internal_order_id']
#     if status == "Canceled":
#
#         amount = full_order_info['total_amount']
#
#         await update_db(user_id, backend_order_id, internal_order_id, amount, status)
#         lang = await users.get_user_lang(user_id)
#         notification_for_user_text = messages.order_was_canceled[lang].format(internal_order_id=internal_order_id, amount=amount, currency=currency)
#         notification_for_admin_text = f'типа вернул {amount} за заказ {internal_order_id} ({backend_order_id}) пользователя {user_id}'
#     if status == 'Partial':
#
#         total_amount = full_order_info['total_amount']
#         quantity = full_order_info['quantity']
#
#         # TODO: хорошо бы remains тоже в бд держать
#         remains = int(order_status_info['remains'])
#
#         cost_per_one_execution = total_amount / quantity
#         amount = cost_per_one_execution * remains
#         internal_order_id = full_order_info['internal_order_id']
#         notification_for_admin_text = (f'Оформляю возврат за частично выполненный заказ:\n\n'
#                 f'Заказ: {internal_order_id} ({backend_order_id}), ID пользователя: {user_id}\n\n'
#                 f'Количество: {quantity}\n'
#                 f'На сумму: {total_amount}\n'
#                 f'Остаток: {remains} единиц\n'
#                 f'Цена одного выполнения: {cost_per_one_execution}\n\n'
#                 f'Возвращаю пользователю: {amount}')
#
#         notification_for_user_text = f'Заказ <b>{internal_order_id}</b> выполнен частично. Возвращено на баланс: {amount} {currency}'
#
#         await update_db(user_id, backend_order_id, internal_order_id, amount, status)
#     try:
#         if notification_for_admin_text:
#             await bot.send_message(config.ADMIN_ID, notification_for_admin_text)
#
#         if notification_for_user_text:
#             await bot.send_message(user_id, notification_for_user_text)
#     except Exception as e:
#         pass


async def return_money_for_canceled_or_partial_order(user_id: int, backend_order_id: str,
                                                     order_status_info: dict) -> bool:

    status = order_status_info.get('status')
    currency = 'RUB'

    # 1. Получаем инфо о заказе
    full_order_info = await orders.get_order_info(user_id, backend_order_id, current_orders=True)
    print('Full order info: ', full_order_info)
    if not full_order_info:
        print('❌ Не найден заказ в текущих:', backend_order_id)
        # Если заказа нет в текущих, возможно он уже в архиве?
        # Проверяем архив, чтобы понять, нужно ли возвращать True для очистки
        archived_info = await orders.get_order_info(user_id, backend_order_id, current_orders=False)
        if archived_info:
            print('⚠️ Заказ уже в архиве, возврат не требуется:', backend_order_id)
            return True  # Заказ уже обработан и в архиве
        return False

    # Если деньги уже помечены как возвращенные в базе
    if full_order_info.get('is_money_returned'):
        print(f'⚠️ Деньги уже возвращены для заказа {backend_order_id}, пропускаю возврат.')
        return True  # Возвращаем True, чтобы главный цикл архивировал этот заказ

    internal_order_id = full_order_info.get('internal_order_id')
    print('✅ Рассчитываю сумму для возврата ', backend_order_id, 'internal_order_id:', internal_order_id)

    # 2. Рассчитываем сумму возврата
    amount = 0.0
    try:
        if status in ["Canceled", "Fail", "Error"]:
            amount = float(full_order_info.get('total_amount', 0))
        elif status == 'Partial':
            total_amount = float(full_order_info.get('total_amount', 0))
            quantity = int(full_order_info.get('quantity', 1))
            # Защита от кривых данных в remains
            remains_raw = order_status_info.get('remains', 0)
            remains = int(float(remains_raw)) if remains_raw else 0

            amount = (total_amount / quantity) * remains
    except (ValueError, TypeError, ZeroDivisionError) as e:
        print(f"❌ Ошибка расчета суммы для {backend_order_id}: {e}")
        return False

    if amount <= 0 and status in ["Canceled", "Fail", "Error"]:
        print(f"⚠️ Сумма возврата 0 для заказа {backend_order_id}, статус {status}")
        # Если статус отменен, но сумма 0 — все равно архивируем
        return True

        # 3. Атомарное обновление баланса
    is_refunded = await update_db(user_id, backend_order_id, internal_order_id, amount, status)
    print(f'🔄 Попытка возврата {round(amount, 2)} RUB для заказа {backend_order_id} пользователю {user_id}. Результат: {is_refunded}')
    # Если возврат не прошел сейчас (например, конкурентный запрос уже изменил флаг)
    if not is_refunded:
        print('⚠️ Возврат не выполнен, возможно уже был обработан ранее для заказа', backend_order_id)
        # Проверяем еще раз: может флаг успел измениться?
        check_info = await orders.get_order_info(user_id, backend_order_id, current_orders=True)
        return check_info.get('is_money_returned', False) if check_info else True

    # 4. Уведомления (только если начисление произошло только что)
    try:
        lang = await users.get_user_lang(user_id)
        if status in ["Canceled", "Fail", "Error"]:
            notification_for_user_text = messages.order_was_canceled[lang].format(
                internal_order_id=internal_order_id, amount=round(amount, 2), currency=currency
            )
            admin_text = f'✅ Возврат {round(amount, 2)} RUB | ID: {backend_order_id} ({internal_order_id}) | User: {user_id}'
        else:
            notification_for_user_text = f'Заказ <b>{internal_order_id}</b> выполнен частично. Возвращено: {round(amount, 2)} {currency}'
            admin_text = f'⚠️ Частичный возврат {round(amount, 2)} RUB | ID: {backend_order_id} ({internal_order_id}) | User: {user_id}'

        await bot.send_message(config.ADMIN_ID, admin_text)
        await bot.send_message(user_id, notification_for_user_text)
    except Exception as e:
        print(f"📦 Ошибка отправки сообщения: {e}")

    return True


# async def update_db(user_id: int, backend_order_id: str, internal_order_id: str, amount: float, order_status: str):
#     meta = {
#         "order_id": backend_order_id,
#         "note": f"Refund for {order_status} order"}
#     try:
#         order_item = await orders_queue.get(internal_order_id)
#         order_item.order_status = OrderStatus.CANCELED if order_status == 'Canceled' else OrderStatus.PARTIAL
#         order_item.is_money_returned = True
#         await orders_queue.update(order_item)
#     except Exception:
#         pass
#
#     await orders.return_money_for_current_order(user_id, backend_order_id, amount)
#
#     user_balance = await users.get_balance(user_id)
#
#     transaction_item = TransactionItem(
#         user_id=user_id,
#         transaction_type=TransactionType.REFUND,
#         amount=amount,
#         balance_after=round((user_balance + amount), 2),
#         meta=meta
#     )
#     await transactions.save(transaction_item)


async def update_db(user_id: int, backend_order_id: str, internal_order_id: str, amount: float,
                    order_status: str) -> bool:
    meta = {
        "order_id": backend_order_id,
        "note": f"Refund for {order_status} order"
    }

    print('🔄 Попытка атомарного возврата денег для заказа', backend_order_id, 'пользователю', user_id)
    # 1. Пытаемся пометить в базе, что деньги возвращены (атомарно)
    # return_money_for_current_order должна использовать find_one_and_update с условием is_money_returned: {'$ne': True}
    new_balance = await orders.return_money_for_current_order(user_id, backend_order_id, amount)

    if new_balance is None:
        print('⚠️ Возврат денег не выполнен для заказа', backend_order_id,)
        return False  # Денег не дали (уже были возвращены)

    # 2. Только если деньги реально начислились, обновляем очередь и транзакции
    try:
        print('✅ Помечаю заказ как возвращенный в главной очереди:', internal_order_id)
        order_item = await orders_queue.get(internal_order_id)
        if order_item:
            print('Заказ найден в главной очереди, обновляю статус и флаг is_money_returned')
            order_item.order_status = OrderStatus.CANCELED if order_status in ['Canceled',
                                                                               'Fail'] else OrderStatus.PARTIAL
            order_item.is_money_returned = True
            await orders_queue.update(order_item)
        else:
            print('❌ Заказ не найден в главной очереди:', internal_order_id)
    except Exception:
        print('❌ Ошибка при обновлении главной очереди в функции update_db, внутренний ID заказа:', internal_order_id)
        pass

    transaction_item = TransactionItem(
        user_id=user_id,
        transaction_type=TransactionType.REFUND,
        amount=amount,
        balance_after=new_balance,
        meta=meta
    )
    await transactions.save(transaction_item)
    return True
#
# async def update_db(user_id: int, backend_order_id: str, internal_order_id: str, amount: float, order_status: str):
#     meta = {
#         "order_id": backend_order_id,
#         "note": f"Refund for {order_status} order"
#     }
#
#     # 1. Обновляем статус заказа (тут можно оставить как есть)
#     try:
#         order_item = await orders_queue.get(internal_order_id)
#         if order_item:
#             order_item.order_status = OrderStatus.CANCELED if order_status == 'Canceled' else OrderStatus.PARTIAL
#             order_item.is_money_returned = True
#             await orders_queue.update(order_item)
#     except Exception:
#         pass
#
#     # 2. Возвращаем деньги и получаем ФИНАЛЬНЫЙ баланс из базы одним махом
#     actual_balance_after = await orders.return_money_for_current_order(user_id, backend_order_id, amount)
#
#     # Если actual_balance_after is None, значит возврат уже был обработан ранее (защита от дублей)
#     if actual_balance_after is not None:
#         transaction_item = TransactionItem(
#             user_id=user_id,
#             transaction_type=TransactionType.REFUND,
#             amount=amount,
#             balance_after=actual_balance_after,  # Используем точное число из БД
#             meta=meta
#         )
#         await transactions.save(transaction_item)
#     else:
#         print(f"⚠️ Попытка повторного возврата для заказа {backend_order_id} отклонена.")


# async def remove_orders_to_history_and_return_money_for_canceled_orders(user_id: int, _orders: dict):
#     for order_id, order_status_info in _orders.items():
#         status = order_status_info['status']
#
#         if status == 'Canceled' or status == 'Partial' or status == 'Fail':
#             await return_money_for_canceled_or_partial_order(user_id, order_id, order_status_info)
#
#         elif status == 'In progress' and status == 'Awaiting':
#             return
#
#         else:
#             await orders.move_orders_to_archive(user_id, order_id)
#             print('Moved order to archive:', order_id)

async def remove_orders_to_history_and_return_money_for_canceled_orders(user_id: int, _orders_info: dict):
    print(f'Пробую переместить заказы в архив и вернуть деньги при необходимости... Количество заказов {len(_orders_info)}')
    for order_id, order_status_info in _orders_info.items():
        status = order_status_info.get('status')

        # 1. Если заказ требует возврата денег
        if status in ['Canceled', 'Partial', 'Fail', 'Error']:
            print(f'🔄 Processing refund for order {order_id} with status {status}...')
            # Пытаемся вернуть деньги
            was_refunded = await return_money_for_canceled_or_partial_order(user_id, order_id, order_status_info)
            print(f'Result: {was_refunded}')
            # Если возврат прошел успешно (или если это дубликат, который уже был обработан)
            if was_refunded:
                await orders.move_orders_to_archive(user_id, order_id)
                print(f'✅ Order {order_id} refunded and moved to archive.')
            else:
                # Если возврат не прошел, МЫ НЕ АРХИВИРУЕМ, чтобы не потерять заказ
                print(f'❌ Order {order_id} NOT refunded. Keeping in current_orders for retry.')

        # 2. Активные заказы — пропускаем
        elif status in ['In progress', 'Awaiting', 'Pending', 'Processing']:
            continue

        # 3. Успешно завершенные — сразу в архив
        else:
            await orders.move_orders_to_archive(user_id, order_id)
            print(f'📦 Order {order_id} (Completed) moved to archive.')

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
#     await orders_queue.update(order_item)


async def update_statuses(user_id: int, order_statuses: dict):
    status_mapping = {
        'In progress': OrderStatus.IN_PROGRESS,
        'Completed': OrderStatus.COMPLETED,
        'Awaiting': OrderStatus.AWAITING,
        'Canceled': OrderStatus.CANCELED,
        'Fail': OrderStatus.FAIL,
        'Error': OrderStatus.FAIL,
        'Partial': OrderStatus.PARTIAL

    }

    for backend_order_id, order_status_info in order_statuses.items():
        raw_status = order_status_info['status']

        status: OrderStatus = status_mapping.get(raw_status)


        # Update in main orders queue
        internal_order_id = await orders.get_internal_order_id_by_backend_order_id(user_id, backend_order_id)
        print('internal_order_id:', internal_order_id, 'backend_order_id:', backend_order_id, 'status:', status)
        order_item = await orders_queue.get(internal_order_id)

        if order_item:
            print('✅Found order_item in main queue')
            order_item.order_status = status
            await orders_queue.update(order_item)

            # Update in user's orders
            order_item = await orders_queue.get(internal_order_id)
            await orders.update_active_order(backend_order_id, order_item)

        else:
            print('❌ Order item not found in main queue')
            await orders.update_order_status(backend_order_id, status)
