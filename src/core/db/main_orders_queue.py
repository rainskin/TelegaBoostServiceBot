from datetime import datetime
import loader
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus


class MainOrdersQueue:

    def __init__(self):
        # Используем default_datetime_format, но обращение к коллекции
        # сделаем через свойство, чтобы не упасть при импорте
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'

    @property
    def collection(self):
        if loader.db is None:
            raise RuntimeError("Database not initialized. Call await loader.init_db() first.")
        return loader.db['main_orders_queue']

    async def save(self, order_item: OrderItem):
        now = datetime.now().strftime(self.default_datetime_format)
        order_item.creation_date = now
        order_item.updated_at = now

        await self.collection.update_one(
            {'internal_order_id': order_item.internal_order_id},
            {'$set': order_item.dict()},
            upsert=True
        )

    async def update(self, order_item: OrderItem):
        order_item.updated_at = datetime.now().strftime(self.default_datetime_format)
        await self.collection.update_one(
            {'internal_order_id': order_item.internal_order_id},
            {'$set': order_item.dict()},
            upsert=True
        )

    async def get(self, internal_order_id: str) -> OrderItem | None:
        data = await self.collection.find_one({'internal_order_id': internal_order_id})
        if data:
            data.pop('_id', None)
            return OrderItem(**data)
        return None

    async def delete(self, internal_order_id: str):
        # Вызываем асинхронный метод через await
        is_deleted = await self.deleted(internal_order_id)
        if not is_deleted:
            await self.collection.update_one(
                {'internal_order_id': internal_order_id},
                {'$set': {
                    'deleted': True,
                    'updated_at': datetime.now().strftime(self.default_datetime_format)
                }}
            )

    async def deleted(self, internal_order_id: str) -> bool:
        doc = await self.collection.find_one({'internal_order_id': internal_order_id})
        return doc.get('deleted', False) if doc else False

    async def get_status(self, internal_order_id: str) -> OrderStatus:
        doc = await self.collection.find_one({'internal_order_id': internal_order_id})
        status = doc.get('order_status', 'unpaid') if doc else 'unpaid'
        return OrderStatus(status)

    async def get_paid_orders(self) -> list[OrderItem]:
        paid_orders = []
        # В Motor .find() возвращает асинхронный курсор
        cursor = self.collection.find({'order_status': OrderStatus.PAID.value})

        async for data in cursor:
            data.pop('_id', None)
            paid_orders.append(OrderItem(**data))

        return paid_orders


# Создаем экземпляр
orders_queue = MainOrdersQueue()