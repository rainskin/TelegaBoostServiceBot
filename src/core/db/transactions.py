from datetime import datetime, timezone
import loader
from config import MONGO_DB_NAME
from core.db.models.transaction_item import TransactionItem

class Transactions:

    def __init__(self):
        # Не привязываем клиент здесь, чтобы избежать Runtime Error (different loop)
        self.default_db_name = MONGO_DB_NAME

    @property
    def collection(self):
        if loader.motor_client is None:
            raise RuntimeError("Motor client not initialized. Call await loader.init_db() first.")
        return loader.motor_client[self.default_db_name]['transactions']

    async def init(self):
        """Метод для асинхронной инициализации (например, создания индексов)"""
        # Создание индекса — асинхронная операция
        await self.collection.create_index('user_id')

    async def save(self, transaction_item: TransactionItem):
        # Устанавливаем текущее время в UTC
        transaction_item.timestamp = datetime.now(timezone.utc)
        # В Pydantic v2 используется model_dump(), в v1 — dict()
        data = transaction_item.model_dump() if hasattr(transaction_item, 'model_dump') else transaction_item.dict()
        await self.collection.insert_one(data)

    async def add_init_transaction(self, transaction_item: TransactionItem):
        doc = await self.collection.find_one({'user_id': transaction_item.user_id})
        if not doc:
            await self.save(transaction_item)


# Экземпляр класса
transactions = Transactions()
