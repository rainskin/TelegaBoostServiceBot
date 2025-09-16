import asyncio
from datetime import datetime, timezone

import loader
from config import MONGO_DB_NAME
from core.db import users
from core.db.models.transaction_item import TransactionItem
from enums.transaction_type import TransactionType


class Transactions:

    def __init__(self):
        self.client = loader.motor_client
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db['transactions']
        self.collection.create_index('user_id')

    async def save(self, transaction_item: TransactionItem):
        transaction_item.timestamp = datetime.now(timezone.utc)
        await self.collection.insert_one(transaction_item.dict())

    async def add_init_transaction(self, transaction_item: TransactionItem):
        doc = await self.collection.find_one({'user_id': transaction_item.user_id})
        if not doc:
            await self.save(transaction_item)


transactions = Transactions()


