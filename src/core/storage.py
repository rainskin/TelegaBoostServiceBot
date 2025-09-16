import motor.motor_asyncio
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

import loader
from config import MONGO_DB_NAME


class MongoStorage(BaseStorage):
    def __init__(self):
        self.client = loader.motor_client
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db['storage']

    async def set_state(self, key: StorageKey, state: StateType = None):
        await self.collection.update_one(
            {'chat_id': key.chat_id, 'user_id': key.user_id},
            {'$set': {'state': state}},
            upsert=True
        )

    async def get_state(self, key: StorageKey) -> StateType:
        document = await self.collection.find_one({'chat_id': key.chat_id, 'user_id': key.user_id})
        return document['state'] if document else None

    async def reset_state(self, key: StorageKey):
        await self.collection.update_one(
            {'chat_id': key.chat_id, 'user_id': key.user_id},
            {'$unset': {'state': ''}}
        )

    async def set_data(self, key: StorageKey, **data):
        data_to_insert = await get_valid_data(**data)

        await self.collection.update_one(
            {'chat_id': key.chat_id, 'user_id': key.user_id},
            {'$set': {'data': data_to_insert}},
            upsert=True
        )

    async def update_data(self, key: StorageKey, **data):
        user_data = await self.get_data(key)
        new_data = await get_valid_data(**data)
        for data_key, data_value in new_data.items():
            user_data[data_key] = data_value

        await self.collection.update_one(
            {'chat_id': key.chat_id, 'user_id': key.user_id},
            {'$set': {'data': user_data}},
            upsert=True
        )

    async def get_data(self, key: StorageKey) -> dict:
        document = await self.collection.find_one({'chat_id': key.chat_id, 'user_id': key.user_id})
        return document.get('data', {}) if document else {}

    async def reset_data(self, key: StorageKey):
        await self.collection.update_one(
            {'chat_id': key.chat_id, 'user_id': key.user_id},
            {'$unset': {'data': ''}}
        )

    async def close(self):
        self.client.close()

    async def delete_data(self, key: StorageKey):
        await self.collection.delete_one({'chat_id': key.chat_id, 'user_id': key.user_id})


async def get_valid_data(**data) -> dict:
    data_to_insert = {}
    for key, value in data.items():
        data_to_insert[key] = value

    return data_to_insert


storage = MongoStorage()
