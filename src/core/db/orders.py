from datetime import datetime
import loader
from core.db import users
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus


class Orders:
    def __init__(self):
        # Используем свойство для доступа к коллекции, чтобы избежать проблем при импорте
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'

    @property
    def collection(self):
        if loader.db_orders is None:
            raise RuntimeError("Database not initialized. Call await loader.init_db() first.")
        return loader.db_orders

    async def get_current_orders(self, user_id) -> dict | None:
        doc = await self.collection.find_one({'user_id': user_id}, {'current_orders': 1})
        return doc.get('current_orders') if doc else None

    async def get_orders_from_archive(self, user_id) -> dict | None:
        doc = await self.collection.find_one({'user_id': user_id}, {'orders_archive': 1})
        return doc.get('orders_archive') if doc else None

    async def new_order(self, platform: str, order_item: OrderItem):
        user_id = order_item.user_id
        backend_order_id = order_item.backend_order_id
        order_id = str(backend_order_id) if backend_order_id else order_item.internal_order_id
        await self.collection.update_one(
            {'user_id': user_id},
            {'$set': {f'current_orders.{order_id}': order_item.dict()}},
            upsert=True
        )

    async def get_not_accepted_orders(self, user_id: int) -> dict | None:
        doc = await self.collection.find_one({'user_id': user_id}, {'not_accepted_orders': 1})
        return doc.get('not_accepted_orders') if doc else None

    async def add_not_accepted_order(self, order_item: OrderItem):
        await self.collection.update_one(
            {'user_id': order_item.user_id},
            {'$set': {f'not_accepted_orders.{order_item.internal_order_id}': order_item.dict()}},
            upsert=True
        )

    async def remove_not_accepted_order(self, user_id: int, order_id: str):
        await self.collection.update_one(
            {'user_id': user_id},
            {'$unset': {f'not_accepted_orders.{order_id}': ''}}
        )

    async def cancel_order(self, user_id: int, order_id: str, not_accepted_orders=False, referral_reward=None):
        field_name = 'not_accepted_orders' if not_accepted_orders else 'current_orders'

        doc = await self.collection.find_one({'user_id': user_id}, {field_name: 1})
        if not doc:
            return

        orders_dict = doc.get(field_name, {})
        order_info = orders_dict.get(order_id)

        if order_info:
            total_amount = order_info.get('total_amount')
            await self.collection.update_one(
                {'user_id': user_id},
                {'$unset': {f'{field_name}.{order_id}': ''}}
            )
            # ВАЖНО: users.add_balance должен быть async!
            await users.add_balance(user_id, float(total_amount))

    # async def return_money_for_current_order(self, user_id: int, order_id: str, amount: float):
    #     # find_one_and_update в Motor возвращает документ или None
    #     doc = await self.collection.find_one_and_update(
    #         {'user_id': user_id, f'current_orders.{order_id}.is_money_returned': {'$ne': True}},
    #         {'$set': {f'current_orders.{order_id}.is_money_returned': True}},
    #         projection={'current_orders': 1},
    #         return_document=True  # В Motor это константа или True для получения новой версии
    #     )
    #
    #     if doc:
    #         current_orders = doc.get('current_orders', {})
    #         if order_id in current_orders:
    #             await users.add_balance(user_id, amount)

    async def return_money_for_current_order(self, user_id: int, order_id: str, amount: float) -> float | None:
        doc = await self.collection.find_one_and_update(
            {'user_id': user_id, f'current_orders.{order_id}.is_money_returned': {'$ne': True}},
            {'$set': {f'current_orders.{order_id}.is_money_returned': True}},
            projection={'current_orders': 1},
            return_document=True
        )

        if doc:
            print("Пометили заказ как 'деньги возвращены'")
            # Если пометили заказ как "деньги возвращены", начисляем баланс
            # и возвращаем то, что ответит нам Users.add_balance
            r = await users.add_balance(user_id, amount)
            print(f"Вернули пользователю {user_id} сумму {amount}. Новый баланс: {r}")
            return r
        return None  # Денег не возвращали (уже были возвращены ранее)

    # не используется
    async def is_first_order(self, user_id: int) -> bool:
        doc = await self.collection.find_one({'user_id': user_id})
        return doc is None

    async def is_order_exist(self, user_id: int, order_id: str, not_accepted_order=False, current_order=False) -> bool:
        field = 'not_accepted_orders' if not_accepted_order else 'current_orders'
        doc = await self.collection.find_one({'user_id': user_id}, {field: 1})
        if not doc:
            return False
        orders_dict = doc.get(field, {})
        return order_id in orders_dict

    async def get_order_info(self, user_id: int, order_id: str, current_orders=False) -> dict | None:
        field = 'current_orders' if current_orders else 'orders_archive'
        doc = await self.collection.find_one({'user_id': user_id}, {field: 1})
        if doc:
            return doc.get(field, {}).get(order_id)
        return None

    async def get_internal_order_id_by_backend_order_id(self, user_id: int, backend_order_id: str) -> str | None:
        order_info = await self.get_order_info(user_id, backend_order_id, current_orders=True)
        if not order_info:
            order_info = await self.get_order_info(user_id, backend_order_id, current_orders=False)
        return order_info.get('internal_order_id') if order_info else None

    async def update_order_status(self, backend_order_id: str, status: OrderStatus):
        print(f"Обновление статуса заказа {backend_order_id} внутри current_orders пользователя")
        # Обновляем в текущих заказах
        doc = await self.collection.find_one_and_update(
            {f'current_orders.{backend_order_id}': {"$exists": True}},
            {"$set": {f'current_orders.{backend_order_id}.order_status': status.value}},
            return_document=True
        )
        # Если в текущих не нашли, ищем в архиве
        if not doc:
            print(f"Заказ {backend_order_id} не найден в current_orders, пробую в orders_archive")
            await self.collection.find_one_and_update(
                {f'orders_archive.{backend_order_id}': {"$exists": True}},
                {"$set": {f'orders_archive.{backend_order_id}.order_status': status.value}}
            )

    async def update_active_order(self, backend_order_id: str, order_item: OrderItem):
        doc = await self.collection.find_one_and_update(
            {f'current_orders.{backend_order_id}': {"$exists": True}},
            {"$set": {f'current_orders.{backend_order_id}': order_item.dict()}},
            return_document=True
        )
        if not doc:
            await self.collection.find_one_and_update(
                {f'orders_archive.{backend_order_id}': {"$exists": True}},
                {"$set": {f'orders_archive.{backend_order_id}': order_item.dict()}}
            )

    async def move_orders_to_archive(self, user_id: int, order_id: str):
        # Конвейеры (pipelines) в update_one поддерживаются Motor точно так же
        pipeline = [
            {
                '$set': {
                    'orders_archive': {
                        '$mergeObjects': [
                            {'$ifNull': ['$orders_archive', {}]},
                            {order_id: f"$current_orders.{order_id}"}
                        ]
                    }
                }
            },
            {
                '$unset': [f'current_orders.{order_id}']
            }
        ]
        await self.collection.update_one({'user_id': user_id}, pipeline)

    async def get_last_internal_order(self, user_id: int):
        doc = await self.collection.find_one({'user_id': user_id}, {'last_internal_order': 1})
        return doc.get('last_internal_order') if doc else None

    async def update_last_internal_order(self, user_id: int, new_order_id: str):
        await self.collection.update_one(
            {'user_id': user_id},
            {"$set": {'last_internal_order': new_order_id}},
            upsert=True
        )


orders = Orders()
