import asyncio

import core
import loader
from busines_logic.order_managment.handle_canceled_orders import \
    remove_orders_to_history_and_return_money_for_canceled_orders, update_statuses
from core.db import orders
from handlers.callback_handlers.main_menu_buttons import get_orders_without_tg_stars_orders
from utils.api import get_order_statuses


async def get_active_users() -> list[int]:
    collection = orders.collection
    print(collection)
    # Запрос: найти документы, где current_orders не равен пустому объекту {}
    # и поле вообще существует
    query = {
        "current_orders": {"$exists": True, "$ne": {}}
    }

    # Извлекаем только user_id, чтобы не тянуть лишние данные (проекция)
    projection = {"user_id": 1, "_id": 0}

    results = collection.find(query, projection)

    # Собираем список ID (используем set, чтобы id не повторялись)
    active_user_ids = set()
    async for doc in results:
        user_id = doc.get("user_id")
        if user_id:
            # В MongoDB $numberLong может прийти как int или спец. объект
            # Извлекаем строковое или числовое значение
            uid = user_id.get("$numberLong") if isinstance(user_id, dict) else user_id
            active_user_ids.add(uid)

    # if 2222223 in active_user_ids:
    #     active_user_ids.remove(2222223)
    #     print('Удален тестовый пользователь 2222223 из списка активных пользователей')
    #

    print(f"Найдено пользователей с активными заказами: {len(active_user_ids)}")
    return list(active_user_ids)


async def update(user_id):
    _orders: dict = await orders.get_current_orders(user_id)
    order_ids = list(_orders.keys())

    if not order_ids:
        return

    print(f"Всего заказов: {len(order_ids)}")

    while order_ids:
        # 1. Берем пачку (первые 50 или сколько осталось)
        current_batch = order_ids[:50]

        # 2. СРАЗУ удаляем эту пачку из основного списка
        # Это гарантирует, что цикл не станет бесконечным
        order_ids = order_ids[50:]

        print(f"Обрабатываю пачку. Осталось в очереди: {len(order_ids)}")

        # 3. Фильтруем заказы
        order_ids_part = await get_orders_without_tg_stars_orders(current_batch)

        if not order_ids_part:
            print("В этой пачке нет подходящих заказов, идем дальше...")
            continue

        # Получаем текущие статусы заказов
        current_order_statuses = await get_order_statuses(order_ids_part)
        print('Обновляю статусы')
        await update_statuses(user_id, current_order_statuses)
        await remove_orders_to_history_and_return_money_for_canceled_orders(user_id, current_order_statuses)


async def run():

    active_user_ids = await get_active_users()

    for user_id in active_user_ids:
        print(f'Обновляю статусы заказов для пользователя {user_id}')
        await update(user_id)


async def run_repeatedly(cooldown: int = 60):
    while True:
        print('Запускаю обновление статусов заказов для всех активных пользователей')
        await run()
        print(f'Завершил обновление статусов заказов. Жду {cooldown} секунд до следующего запуска.')
        await asyncio.sleep(cooldown)

#
# if __name__ == "__main__":
#     asyncio.run(run_repeatedly())

