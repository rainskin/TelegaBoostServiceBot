import motor.motor_asyncio
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey
import loader
from config import MONGO_DB_NAME


class MongoStorage(BaseStorage):
    def __init__(self):
        self.db_name = MONGO_DB_NAME

    @property
    def collection(self):
        if loader.motor_client is None:
            raise RuntimeError("Motor client is not initialized. Call await loader.init_db() first.")
        return loader.motor_client[self.db_name]['storage']

    async def set_state(self, key: StorageKey, state: StateType = None):
        state_to_save = state.state if hasattr(state, 'state') else state
        await self.collection.update_one(
            {'chat_id': key.chat_id, 'user_id': key.user_id},
            {'$set': {'state': state_to_save}},
            upsert=True
        )

    async def get_state(self, key: StorageKey) -> str | None:
        document = await self.collection.find_one({'chat_id': key.chat_id, 'user_id': key.user_id})
        return document.get('state') if document else None

    # ИСПРАВЛЕНО: добавлена поддержка и словаря, и именованных аргументов
    async def set_data(self, key: StorageKey, data: dict = None, **kwargs):
        if data is None:
            data = {}
        data.update(kwargs)  # Объединяем словарь и доп. аргументы

        await self.collection.update_one(
            {'chat_id': key.chat_id, 'user_id': key.user_id},
            {'$set': {'data': data}},
            upsert=True
        )

    async def get_data(self, key: StorageKey) -> dict:
        document = await self.collection.find_one({'chat_id': key.chat_id, 'user_id': key.user_id})
        return document.get('data', {}) if document else {}

    # ИСПРАВЛЕНО: теперь принимает **kwargs как старый класс
    async def update_data(self, key: StorageKey, data: dict = None, **kwargs):
        if data is None:
            data = {}

        current_data = await self.get_data(key)
        current_data.update(data)
        current_data.update(kwargs)  # Теперь сработает msgs_to_delete=...

        await self.set_data(key, data=current_data)

    async def close(self):
        if loader.motor_client:
            loader.motor_client.close()

    async def delete_data(self, key: StorageKey):
        await self.collection.update_one(
            {'chat_id': key.chat_id, 'user_id': key.user_id},
            {'$unset': {'data': ''}}
        )

    async def reset_state(self, key: StorageKey):
        await self.set_state(key, state=None)

    async def reset_data(self, key: StorageKey):
        await self.collection.update_one(
            {'chat_id': key.chat_id, 'user_id': key.user_id},
            {'$unset': {'data': ''}}
        )


# Создаем экземпляр
storage = MongoStorage()